"""Core engine v2: storage (SQLite), Bayesian skill estimation (Brain Twin), behaviour signals,
adaptive difficulty, learning plan, projection with uncertainty, spot-the-error probes."""
import difflib
import json
import math
import random
import re
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

import tasks_custom  # noqa: F401  (registers optional extra dimensions)
from tasks import REGISTRY

DB = Path("braintwin.db")
LEVELS = 5
RETENTION_DAYS = 90
CALIBRATION_TRIALS = 15

DIMENSIONS = {n: v["desc"] for n, v in REGISTRY.items()}
CHANCE = {n: v["chance"] for n, v in REGISTRY.items()}

GRID = np.linspace(0, 100, 101)  # skill scale 0-100
DECAY = 0.97                     # forgetting factor: recent trials weigh more
SCALE = 12.0                     # slope of the success curve


# ----------------------------------------------------------------- storage
def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS trials(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, dim TEXT, level INT,
        correct INT, rt REAL, tlimit REAL, hint INT,
        changes INT DEFAULT 0, t_first REAL, mood INT, abandoned INT DEFAULT 0)""")
    existing = {r["name"] for r in c.execute("PRAGMA table_info(trials)")}
    for col, typ in {"changes": "INT DEFAULT 0", "t_first": "REAL", "mood": "INT",
                     "abandoned": "INT DEFAULT 0"}.items():  # migrate databases created by v1
        if col not in existing:
            c.execute(f"ALTER TABLE trials ADD COLUMN {col} {typ}")
    c.execute("""CREATE TABLE IF NOT EXISTS chat(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, role TEXT, text TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS goals(
        user TEXT, dim TEXT, target REAL, PRIMARY KEY(user, dim))""")
    c.execute("""CREATE TABLE IF NOT EXISTS probes(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, claim TEXT, flawed INT,
        verified INT, action TEXT, score REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings(
        user TEXT PRIMARY KEY, ts REAL, age_band TEXT, fun INT, reading INT, calm INT, guardian INT,
        age INT, profile TEXT DEFAULT 'typical', focus INT DEFAULT 0, severity TEXT DEFAULT 'mild')""")
    existing_s = {r["name"] for r in c.execute("PRAGMA table_info(settings)")}
    for col, typ in {"age": "INT", "profile": "TEXT DEFAULT 'typical'",
                     "focus": "INT DEFAULT 0", "severity": "TEXT DEFAULT 'mild'"}.items():  # migrate old databases
        if col not in existing_s:
            c.execute(f"ALTER TABLE settings ADD COLUMN {col} {typ}")
    c.execute("""CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, category TEXT, item_id INT, level INT, correct INT,
        domain TEXT DEFAULT 'social')""")
    if "domain" not in {r["name"] for r in c.execute("PRAGMA table_info(activities)")}:  # migrate v4 databases
        c.execute("ALTER TABLE activities ADD COLUMN domain TEXT DEFAULT 'social'")
    c.execute("""CREATE TABLE IF NOT EXISTS kv(
        user TEXT, k TEXT, v TEXT, ts REAL, PRIMARY KEY(user, k))""")  # small saved things: my day plan, my calm kit...
    c.execute("""CREATE TABLE IF NOT EXISTS writing(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, text_id INT, level INT, mode TEXT, attempt INT,
        word_acc REAL, letter_acc REAL, n_words INT, n_wrong INT, errors TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reading(
        id INTEGER PRIMARY KEY, user TEXT, ts REAL, text_id INT, level INT, attempt INT,
        accuracy REAL, n_words INT, n_wrong INT)""")
    return c


def log_trial(user, t, correct, rt, hint, changes=0, t_first=None, mood=None, abandoned=False):
    c = conn()
    c.execute("""INSERT INTO trials(user,ts,dim,level,correct,rt,tlimit,hint,changes,t_first,mood,abandoned)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
              (user, time.time(), t["dim"], t["level"], int(correct), float(rt), t["tlimit"],
               int(hint), int(changes), t_first, mood, int(abandoned)))
    c.commit(); c.close()


def log_chat(user, role, text):
    c = conn()
    c.execute("INSERT INTO chat(user,ts,role,text) VALUES (?,?,?,?)", (user, time.time(), role, text))
    c.commit(); c.close()


def get_chat(user):
    c = conn()
    rows = c.execute("SELECT role,text FROM chat WHERE user=? ORDER BY ts", (user,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def trials_df(user):
    c = conn()
    df = pd.read_sql("SELECT * FROM trials WHERE user=? ORDER BY ts", c, params=(user,))
    c.close()
    return df


def get_probes(user):
    c = conn()
    df = pd.read_sql("SELECT * FROM probes WHERE user=? ORDER BY ts", c, params=(user,))
    c.close()
    return df


def get_goals(user):
    c = conn()
    rows = c.execute("SELECT dim,target FROM goals WHERE user=?", (user,)).fetchall()
    c.close()
    g = {d: 70.0 for d in DIMENSIONS}
    g.update({r["dim"]: r["target"] for r in rows if r["dim"] in DIMENSIONS})
    return g


def set_goal(user, dim, target):
    c = conn()
    c.execute("INSERT OR REPLACE INTO goals(user,dim,target) VALUES (?,?,?)", (user, dim, target))
    c.commit(); c.close()


def delete_user(user):
    c = conn()
    for table in ("trials", "chat", "goals", "probes", "settings", "reading", "activities", "writing", "kv"):
        c.execute(f"DELETE FROM {table} WHERE user=?", (user,))
    c.commit(); c.close()


def purge_old(days=RETENTION_DAYS):
    """Retention policy: automatically delete data older than `days`."""
    limit = time.time() - days * 86400
    c = conn()
    for table in ("trials", "chat", "probes", "reading", "activities", "writing", "kv"):
        c.execute(f"DELETE FROM {table} WHERE ts<?", (limit,))
    c.commit(); c.close()


def export_user(user):
    return json.dumps({"trials": trials_df(user).to_dict("records"),
                       "chat": get_chat(user), "goals": get_goals(user),
                       "challenges": get_probes(user).to_dict("records"),
                       "support_settings": get_settings(user),
                       "reading_practice": get_reading(user).to_dict("records"),
                       "writing_practice": get_writing(user).to_dict("records"),
                       "saved_choices": kv_all(user),
                       "practice_questions": get_activities(user).to_dict("records")}, indent=2, default=str)


# ------------------------------------------------- Brain Twin (estimation)
def evidence(correct, rt, tlimit, hint):
    """Trial outcome in [0,1]: wrong=0, correct+slow=0.85, correct=1, hint caps at 0.7.
    (Penalties are mild on purpose: validation by simulation showed that harsher values made always-slow
    users collapse to very low estimates.)"""
    if not correct:
        return 0.0
    c = 1.0 if rt <= tlimit else 0.85
    return min(c, 0.7) if hint else c


def update_logp(logp, level, c, chance):
    """One Bayesian update on the grid.
    P(success | s, level) = chance + (1-chance) * sigmoid((s - difficulty)/SCALE), difficulty=(level-0.5)*20.
    Exponential forgetting (DECAY) widens uncertainty when the user stops training."""
    d = (level - 0.5) * 20
    p = chance + (1 - chance) / (1 + np.exp(-(GRID - d) / SCALE))
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return DECAY * logp + c * np.log(p) + (1 - c) * np.log(1 - p)


def summarize(logp):
    """Posterior mean and 95% credible interval."""
    post = np.exp(logp - logp.max())
    post /= post.sum()
    cdf = np.cumsum(post)
    return (float((post * GRID).sum()),
            float(GRID[min(np.searchsorted(cdf, 0.025), 100)]),
            float(GRID[min(np.searchsorted(cdf, 0.975), 100)]))


def estimate_history(df_dim, dim):
    chance = CHANCE[dim]
    logp = np.zeros_like(GRID)
    out = []
    for i, r in enumerate(df_dim.itertuples(), start=1):
        logp = update_logp(logp, r.level, evidence(r.correct, r.rt, r.tlimit, r.hint), chance)
        m, lo, hi = summarize(logp)
        out.append(dict(ts=r.ts, attempt=i, dim=dim, mean=m, lo=lo, hi=hi))
    return out


def build_twin(user):
    """Returns (profile dict, history DataFrame, raw trials DataFrame)."""
    df = trials_df(user)
    est = df[df.abandoned.fillna(0) == 0] if len(df) else df  # abandoned trials do not move the estimate
    profile, hist = {}, []
    for dim in DIMENSIONS:
        rows = est[est.dim == dim] if len(est) else est
        if len(rows) == 0:
            profile[dim] = dict(mean=50.0, lo=0.0, hi=100.0, n=0)
            continue
        h = estimate_history(rows, dim)
        hist += h
        profile[dim] = dict(mean=h[-1]["mean"], lo=h[-1]["lo"], hi=h[-1]["hi"], n=len(rows))
    return profile, pd.DataFrame(hist), df


def behaviour(df):
    """Behaviour signals (non-biometric), all computed from interaction logs."""
    if df is None or len(df) == 0:
        return None
    ab = df.abandoned.fillna(0)
    done = df[ab == 0]
    out = dict(n=len(done), abandon_rate=float(ab.mean()), hint_rate=None, avg_answer_changes=None,
               hesitation=None, speed_ratio=None, rt_variability=None)
    if len(done):
        out["hint_rate"] = float(done.hint.mean())
        out["avg_answer_changes"] = float(done.changes.fillna(0).mean())
        ratio = (done.t_first / done.rt).replace([np.inf, -np.inf], np.nan).dropna()
        out["hesitation"] = float(ratio.median()) if len(ratio) else None  # share of time before 1st choice
        out["speed_ratio"] = float((done.rt / done.tlimit).median())       # <1 = within time limit
        ok = done[done.correct == 1]
        if len(ok) > 2 and ok.rt.mean() > 0:
            out["rt_variability"] = float(ok.rt.std() / ok.rt.mean())
    return out


def expected_success(dim, level, skill):
    ch = CHANCE[dim]
    d = (level - 0.5) * 20
    return ch + (1 - ch) / (1 + math.exp(-(skill - d) / SCALE))


# ------------------------------------------------------- adaptive learning
def next_level(mean):
    """Pick the level where expected success is high but still challenging."""
    return int(np.clip(round((mean - 5) / 20 + 0.5), 1, LEVELS))


def make_plan(profile, goals):
    plan = []
    for dim, p in profile.items():
        gap = max(goals[dim] - p["mean"], 0)
        width = p["hi"] - p["lo"]
        priority = 0.6 * gap + 0.4 * width
        reason = ("it is the furthest from your goal" if gap >= width / 2
                  else "we are still unsure about your level there")
        plan.append(dict(dim=dim, priority=round(priority, 1), level=next_level(p["mean"]),
                         target=goals[dim], gap=round(gap, 1), reason=reason,
                         n_trials=5 if p["n"] < 10 else 8))
    return sorted(plan, key=lambda x: -x["priority"])


def pick_dimension(profile, plan):
    """Calibration phase: round-robin on the least-tested dimension, then follow the plan."""
    total = sum(p["n"] for p in profile.values())
    if total < CALIBRATION_TRIALS:
        names = list(profile)
        return min(names, key=lambda d: (profile[d]["n"], names.index(d)))
    return plan[0]["dim"]


def explain_trial(dim, level, profile, goals, mode, mood_adjusted=False):
    """Explainability: tell the user WHY this exercise was chosen, with numbers."""
    p = profile[dim]
    exp = expected_success(dim, level, p["mean"])
    if mode == "calibration":
        why = (f"Calibration: we need a first estimate for every dimension "
               f"(you have {p['n']} exercise(s) in {dim}).")
    elif mode == "priority":
        why = (f"{dim} is your top priority: about {p['mean']:.0f}% now (range {p['lo']:.0f}-{p['hi']:.0f}), "
               f"goal {goals[dim]:.0f}%.")
    else:
        why = f"You chose {dim} (about {p['mean']:.0f}% now, range {p['lo']:.0f}-{p['hi']:.0f})."
    txt = (f"{why} Level {level}/5 is picked so you succeed about {exp * 100:.0f}% of the time: "
           f"challenging enough to learn, not discouraging.")
    if mood_adjusted:
        txt += " You said you feel low on energy today, so we made it one level easier."
    return txt


def project(hist_dim, horizon=15, shrink=0.5, window=20):
    """Optional projection WITH uncertainty. Linear trend on the last `window` estimates,
    shrunk by `shrink` (to avoid over-optimism), band = prediction interval + current posterior width.
    Returns None if fewer than 8 points. A projection is a scenario, never a promise."""
    h = pd.DataFrame(hist_dim).tail(window)
    if len(h) < 8:
        return None
    x = h["attempt"].to_numpy(float)
    y = h["mean"].to_numpy(float)
    slope, icpt = np.polyfit(x, y, 1)
    n = len(x)
    s = math.sqrt(max(((y - (slope * x + icpt)) ** 2).sum() / (n - 2), 1e-6))
    sxx = ((x - x.mean()) ** 2).sum()
    fx = np.arange(x[-1] + 1, x[-1] + horizon + 1)
    pred = np.clip(y[-1] + shrink * slope * (fx - x[-1]), 0, 100)
    se = s * np.sqrt(1 + 1 / n + (fx - x.mean()) ** 2 / sxx)
    half = (h["hi"].iloc[-1] - h["lo"].iloc[-1]) / 2
    band = np.sqrt((1.96 * se) ** 2 + half ** 2)
    return pd.DataFrame(dict(attempt=fx, mean=pred, lo=np.clip(pred - band, 0, 100),
                             hi=np.clip(pred + band, 0, 100)))


# --------------------------------- spot-the-error challenges (collaboration)
def make_probe(profile, rng=random):
    """A verifiable claim about the user's OWN profile; half of them are deliberately wrong.
    Measures whether the user verifies AI output instead of trusting it blindly."""
    dims = [d for d, p in profile.items() if p["n"] > 0]
    if len(dims) < 2:
        return None
    flawed = rng.random() < 0.5
    means = {d: profile[d]["mean"] for d in dims}
    best, worst = max(means, key=means.get), min(means, key=means.get)
    if best != worst and rng.random() < 0.5:
        d = worst if flawed else best
        return dict(kind="rank", dim=d, value=None, flawed=flawed,
                    claim=f"Your strongest area right now is {d}.")
    d = rng.choice(dims)
    m = round(means[d])
    shown = m
    if flawed:
        shown = m - rng.randint(20, 30) if m >= 50 else m + rng.randint(20, 30)
    return dict(kind="value", dim=d, value=shown, flawed=flawed,
                claim=f"Your estimate for {d} is about {shown}%.")


def probe_score(flawed, action, verified):
    """Right decision (accept a true claim / flag a wrong one) = 1.0 if verified, 0.8 otherwise.
    Wrong decision = 0.3 if verified, 0.0 if blind."""
    correct = (action == "flag") == bool(flawed)
    if correct:
        return 1.0 if verified else 0.8
    return 0.3 if verified else 0.0


def log_probe(user, probe, action, verified):
    sc = probe_score(probe["flawed"], action, verified)
    c = conn()
    c.execute("INSERT INTO probes(user,ts,claim,flawed,verified,action,score) VALUES (?,?,?,?,?,?,?)",
              (user, time.time(), probe["claim"], int(probe["flawed"]), int(verified), action, sc))
    c.commit(); c.close()
    return sc


# --------------------------------------------------------- task generation
def trial_signature(t):
    return f"{t['dim']}|{t['prompt']}|{t.get('html')}|{t.get('memorize')}"


def make_trial(dim, level, rng=random, avoid=()):
    """New exercise. `avoid` = signatures of recent exercises: we regenerate (up to 30 times) so that the
    child does not get the same exercise twice in a short time."""
    avoid = set(avoid)
    for _ in range(30):
        t = dict(dim=dim, level=level, html=None, memorize=None, show_s=0.0, tlimit=12.0)
        t.update(REGISTRY[dim]["fn"](level, rng))
        t["answer"] = str(t["answer"])
        t["choices"] = [str(c) for c in t["choices"]]
        t["sig"] = trial_signature(t)
        if t["sig"] not in avoid:
            break
    return t


# ------------------------------------------------ profiles and settings
AGE_BANDS = ["5-7", "8-10", "11-13", "14-17", "18+"]
MAX_LEVEL_BY_AGE = {"5-7": 3, "8-10": 4}
PROFILES = ("typical", "autism", "dyslexia", "adhd")

LABELS_EXPLICIT = {"typical": "🙂 Typical development", "autism": "🌈 Autism", "dyslexia": "📖 Dyslexia",
                   "adhd": "⚡ ADHD"}
LABELS_SAFE = {"typical": "🙂 No specific need", "autism": "🌈 Calm & routine support",
               "dyslexia": "📖 Reading support", "adhd": "⚡ Focus & movement support"}


def profile_label(key):
    """Wording of the profile choice. Set SAFE_LABELS=1 for strictly non-clinical wording (brief-friendly)."""
    import os
    return (LABELS_SAFE if os.getenv("SAFE_LABELS") == "1" else LABELS_EXPLICIT)[key]


def age_band_for(age):
    age = int(age)
    return "5-7" if age <= 7 else "8-10" if age <= 10 else "11-13" if age <= 13 else "14-17" if age <= 17 else "18+"


def max_level(age_band):
    """Younger users start with a lower difficulty ceiling."""
    return MAX_LEVEL_BY_AGE.get(age_band, LEVELS)


def social_cap(age):
    return 2 if int(age or 8) <= 7 else 3


def is_minor(age_band):
    return age_band != "18+"


def default_fun(age_band):
    return age_band in ("5-7", "8-10", "11-13")


# ------------------------------------------------ degree (level of support), chosen by the parent / guardian
SEVERITIES = ("mild", "moderate", "severe")
SEVERITY_LABELS = {"mild": "🟢 Mild (light support)", "moderate": "🟡 Moderate (some support)",
                   "severe": "🟠 Severe (a lot of support)"}
SEVERITY_LABELS_SAFE = {"mild": "🟢 Light support", "moderate": "🟡 Some support", "severe": "🟠 A lot of support"}
# what the degree changes: questions per series, highest practice level, brain-game ceiling, hints
SEVERITY_RULES = {"mild": dict(plan=5, q_cap=3, brain_cap=5, hint="on demand"),
                  "moderate": dict(plan=4, q_cap=3, brain_cap=4, hint="offered"),
                  "severe": dict(plan=3, q_cap=2, brain_cap=2, hint="always shown")}


def severity_label(key):
    import os
    return (SEVERITY_LABELS_SAFE if os.getenv("SAFE_LABELS") == "1" else SEVERITY_LABELS).get(key or "mild")


def severity_rules(severity, profile="typical"):
    """Typical profile: no degree (always the 'mild' rules)."""
    return SEVERITY_RULES["mild" if profile == "typical" else (severity or "mild")]


def profile_defaults(profile, age, severity="mild"):
    """Comfort options pre-selected for each declared profile and degree (the parent can change them)."""
    band = age_band_for(age)
    severe = profile != "typical" and severity == "severe"
    return dict(fun=(default_fun(band) and profile != "autism") or (profile == "adhd" and is_minor(band)),
                reading=(profile == "dyslexia"), calm=(profile == "autism") or (severe and profile == "dyslexia"),
                focus=(profile == "adhd"))


def list_profiles():
    c = conn()
    rows = c.execute("SELECT user FROM settings ORDER BY user").fetchall()
    c.close()
    return [r["user"] for r in rows]


def get_settings(user):
    """Profile declared by the parent/guardian + comfort options. The app never diagnoses, screens or infers."""
    c = conn()
    r = c.execute("SELECT * FROM settings WHERE user=?", (user,)).fetchone()
    c.close()
    if not r:
        return None
    return dict(age=r["age"], age_band=r["age_band"], profile=r["profile"] or "typical", fun=bool(r["fun"]),
                reading=bool(r["reading"]), calm=bool(r["calm"]), guardian=bool(r["guardian"]),
                focus=bool(r["focus"]), severity=r["severity"] or "mild")


def set_settings(user, age, profile, fun, reading, calm, guardian, focus=False, severity="mild"):
    c = conn()
    c.execute("""INSERT OR REPLACE INTO settings(user,ts,age_band,fun,reading,calm,guardian,age,profile,focus,severity)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (user, time.time(), age_band_for(age), int(fun), int(reading), int(calm), int(guardian),
               int(age), profile, int(focus), severity if severity in SEVERITIES else "mild"))
    c.commit(); c.close()


def kv_get(user, k, default=None):
    c = conn()
    r = c.execute("SELECT v FROM kv WHERE user=? AND k=?", (user, k)).fetchone()
    c.close()
    return json.loads(r["v"]) if r else default


def kv_set(user, k, value):
    c = conn()
    c.execute("INSERT OR REPLACE INTO kv(user,k,v,ts) VALUES (?,?,?,?)", (user, k, json.dumps(value), time.time()))
    c.commit(); c.close()


def kv_all(user):
    c = conn()
    rows = c.execute("SELECT k, v FROM kv WHERE user=?", (user,)).fetchall()
    c.close()
    return {r["k"]: json.loads(r["v"]) for r in rows}


# practice-question activities are stored in one table, separated by domain:
#   social = feelings & routines (autism profile), focus = focus & self-control (ADHD), words = word games (dyslexia)
DOMAINS = ("social", "focus", "words")


def log_activity(user, category, item_id, level, correct, domain="social"):
    c = conn()
    c.execute("INSERT INTO activities(user,ts,category,item_id,level,correct,domain) VALUES (?,?,?,?,?,?,?)",
              (user, time.time(), category, int(item_id), int(level), int(correct), domain))
    c.commit(); c.close()


def get_activities(user, domain=None):
    c = conn()
    df = pd.read_sql("SELECT * FROM activities WHERE user=? ORDER BY ts", c, params=(user,))
    c.close()
    if len(df):
        df["domain"] = df["domain"].fillna("social")
    return df[df.domain == domain].reset_index(drop=True) if domain else df


def practice_summary(df_act):
    """{domain: {category: % answered well}} for the dashboard and the coach."""
    if df_act is None or len(df_act) == 0:
        return {}
    return {d: {c: round(float(g.correct.mean()) * 100) for c, g in dd.groupby("category")}
            for d, dd in df_act.groupby("domain")}


# ------------------------------------------------ writing practice (look, hide, write)
def log_writing(user, text_id, level, mode, attempt, res):
    c = conn()
    c.execute("""INSERT INTO writing(user,ts,text_id,level,mode,attempt,word_acc,letter_acc,n_words,n_wrong,errors)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (user, time.time(), int(text_id), int(level), mode, int(attempt), float(res["word_acc"]),
               float(res["letter_acc"]), int(res["n_words"]), int(res["n_wrong"]), json.dumps(res["errors"])))
    c.commit(); c.close()


def get_writing(user):
    c = conn()
    df = pd.read_sql("SELECT * FROM writing WHERE user=? ORDER BY ts", c, params=(user,))
    c.close()
    return df


def writing_summary(df_w):
    if df_w is None or len(df_w) == 0:
        return None
    a1, a2 = df_w[df_w.attempt == 1], df_w[df_w.attempt == 2]
    return dict(sentences=int(len(a1)),
                first_try_words_correct=round(float(a1.word_acc.mean()) * 100) if len(a1) else None,
                second_try_words_correct=round(float(a2.word_acc.mean()) * 100) if len(a2) else None)


# ------------------------------------------------ reading practice: read, write, fix
READING_TEXTS = {
    1: ["The cat sat on the mat.", "I like to play in the sun.", "My dog runs very fast.",
        "We eat bread and jam.", "The sun is hot today.", "A frog can jump high.", "The pig is in the mud.",
        "I have a red ball.", "Mum can see the moon.", "The fish is in the pond.", "We sit on the rug."],
    2: ["The little bird sings a happy song every morning.", "My friend has a red bicycle and a blue hat.",
        "We went to the park after school today.", "My sister bakes a warm cake on Sundays.",
        "The big brown horse runs across the green field.", "Grandpa plants carrots in his small garden.",
        "The kitten sleeps on a soft pillow.", "We sing songs together in the car.",
        "A yellow duck swims across the pond."],
    3: ["Yesterday our teacher showed us a beautiful picture of a rainbow.",
        "The children carefully carried their bags across the busy street.",
        "Every evening my grandmother reads a wonderful story before bedtime.",
        "After lunch we planted tiny flowers in the school garden.",
        "The firefighters quickly climbed the long ladder to help.",
        "My uncle cooked a delicious soup with fresh vegetables.",
        "On Saturday we built a snowman with a funny orange nose."],
    4: ["Although it was raining heavily, the explorers continued their adventure through the forest.",
        "The scientist patiently measured the temperature of the water every single morning.",
        "Our neighbour built a wooden boat and sailed along the quiet river.",
        "The museum guide explained how dinosaurs lived millions of years ago.",
        "When the bell rang, the students walked calmly to the playground.",
        "My cousin practised the guitar until she could play the whole song."],
    5: ["Despite the unexpected difficulties, the determined students completed their extraordinary project "
        "before the deadline.",
        "The enormous mountain looked mysterious in the early morning fog, although the forecast promised sunshine.",
        "Throughout the whole afternoon, the curious children investigated the strange noises coming from the "
        "old library.",
        "The astronaut described how the planet looked brilliant and peaceful from space.",
        "Although the recipe seemed complicated, the children prepared a delicious chocolate dessert."],
}


def log_reading(user, text_id, level, attempt, accuracy, n_words, n_wrong):
    c = conn()
    c.execute("INSERT INTO reading(user,ts,text_id,level,attempt,accuracy,n_words,n_wrong) VALUES (?,?,?,?,?,?,?,?)",
              (user, time.time(), int(text_id), int(level), int(attempt), float(accuracy), int(n_words), int(n_wrong)))
    c.commit(); c.close()


def get_reading(user):
    c = conn()
    df = pd.read_sql("SELECT * FROM reading WHERE user=? ORDER BY ts", c, params=(user,))
    c.close()
    return df


def reading_level(df_r, cap=LEVELS):
    """Level of the next sentence from the last 3 FIRST attempts: >=90% -> harder, <=50% -> easier."""
    if df_r is None or len(df_r) == 0:
        return 1
    first = df_r[df_r.attempt == 1].tail(3)
    if first.empty:
        return 1
    lvl = int(first.level.iloc[-1])
    acc = float(first.accuracy.mean())
    if len(first) >= 2 and acc >= 0.9:
        lvl += 1
    elif acc <= 0.5:
        lvl -= 1
    return int(np.clip(lvl, 1, cap))


def pick_text(level, used=(), rng=random):
    """Never-read sentences first; when all are read, the one read the longest time ago (no quick repeats)."""
    options = [(level * 100 + i, t) for i, t in enumerate(READING_TEXTS[level])]
    used = list(used)
    fresh = [o for o in options if o[0] not in set(used)]
    if fresh:
        return rng.choice(fresh)
    last = {tid: k for k, tid in enumerate(used)}
    return min(options, key=lambda o: last.get(o[0], -1))


def _words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def compare_reading(original, typed, tolerance=1.0):
    """Word-by-word comparison (case and punctuation ignored).
    Each original word is 'ok', 'changed' (typed differently) or 'missing'.
    tolerance < 1 (e.g. 0.8 for voice) accepts near-matches, because speech recognition is noisy."""
    a, b = _words(original), _words(typed)
    ops = difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()
    marks = []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            marks += [dict(word=w, status="ok", got=w) for w in a[i1:i2]]
        elif tag in ("replace", "delete"):
            got = b[j1:j2]
            for k, w in enumerate(a[i1:i2]):
                g = got[k] if k < len(got) else ""
                near = bool(g) and tolerance < 1.0 and difflib.SequenceMatcher(a=w, b=g).ratio() >= tolerance
                marks.append(dict(word=w, status="ok" if near else ("changed" if g else "missing"), got=g))
    n = len(a)
    ok = sum(m["status"] == "ok" for m in marks)
    return dict(accuracy=(ok / n if n else 0.0), n_words=n, n_wrong=n - ok, marks=marks)


def reading_feedback(res):
    """Gentle, non-judgemental feedback."""
    if res["n_words"] and res["n_wrong"] == 0:
        return "Perfect! Every word matches. 🌟"
    todo = [m for m in res["marks"] if m["status"] != "ok"][:4]
    bits = [f"'{m['word']}'" + (f" (you wrote '{m['got']}')" if m["got"] else " (missing)") for m in todo]
    return (f"You got {res['n_words'] - res['n_wrong']} of {res['n_words']} words right. "
            f"Let's polish: {', '.join(bits)}.")


def reading_summary(df_r):
    if df_r is None or len(df_r) == 0:
        return None
    a1, a2 = df_r[df_r.attempt == 1], df_r[df_r.attempt == 2]
    return dict(sentences=int(df_r.text_id.nunique()),
                first_try_accuracy=round(float(a1.accuracy.mean()) * 100) if len(a1) else None,
                second_try_accuracy=round(float(a2.accuracy.mean()) * 100) if len(a2) else None)


def correction_script(name, text, marks):
    """What the voice agent says after a reading with mistakes: encouragement, the whole sentence read slowly,
    then the tricky words one by one."""
    wrong = [m["word"] for m in marks if m["status"] != "ok"][:4]
    intro = f"Good try{', ' + name if name else ''}. Let's read it together. "
    drills = " ".join(f"{w}, {w}." for w in wrong)
    return intro + text + (" Let's practise these words: " + drills if drills else "")
