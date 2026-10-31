import json
import random
import re
import time
import uuid
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

import coach
import collab
import engine
import focus_content
import games_content
import literacy
import stt
import support_content
import ui_extra
import visual_games
from practice import level_from_history

st.set_page_config(page_title="Cognitive Growth Agent", page_icon="🧠", layout="wide")
engine.purge_old()  # retention policy
ss = st.session_state

MOODS = {1: "😞 very low energy", 2: "😕 low", 3: "😐 okay", 4: "🙂 good", 5: "😄 great"}
ROUND = 5  # exercises per round in fun mode
PRAISE = ["Great job!", "Awesome!", "You got it!", "Super!", "Well done!"]
NEW = "➕ New child / profile"
BAND_AGE = {"5-7": 6, "8-10": 9, "11-13": 12, "14-17": 15, "18+": 30}


def speak(text, rate=1.0):
    """Browser text-to-speech (output only)."""
    clean = re.sub(r"[*_`#]", "", text)
    components.html("<script>const u=new SpeechSynthesisUtterance(" + json.dumps(clean) + ");"
                    f"u.lang='en-US';u.rate={rate};window.speechSynthesis.cancel();"
                    "window.speechSynthesis.speak(u);</script>", height=0)


def on_answer():
    """Behaviour signals: time to first choice and number of answer changes."""
    if not ss.get("first_done"):
        ss.first_done = True
        ss.t_first = time.time() - ss.t0
    else:
        ss.changes = ss.get("changes", 0) + 1


def inject_css(S):
    css = ""
    if S["reading"]:  # reading support: friendly font, bigger text, more spacing
        css += ("@import url('https://fonts.googleapis.com/css2?family=Lexend&display=swap');"
                ".stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp textarea, .stApp input"
                "{font-family:'Lexend','Verdana','Arial',sans-serif; font-size:1.12rem; letter-spacing:0.03em;"
                "line-height:1.8;} ")
    if S["calm"]:     # calm: no animations or transitions
        css += "*{animation:none !important; transition:none !important;} "
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def marks_html(marks):
    parts = []
    for m in marks:
        if m["status"] == "ok":
            parts.append(f"<span style='color:#2e7d32'>{m['word']}</span>")
        elif m["status"] == "changed":
            parts.append(f"<span style='color:#ef6c00'><s>{m['got']}</s> → <b>{m['word']}</b></span>")
        else:
            parts.append(f"<span style='color:#c62828'>[<b>{m['word']}</b>]</span>")
    return ("<div style='font-size:1.4rem;line-height:2.2;letter-spacing:.04em'>" + " ".join(parts) + "</div>")


def feedback_text(ok, answer, rt, tlimit, S, extra=""):
    if S["fun"]:
        txt = f"{random.choice(PRAISE)} ⭐" if ok else f"Nice try! The answer was {answer}. Let's go again!"
    elif S["calm"]:
        txt = "Correct." if ok else f"Not this time — the answer was {answer}. That's okay."
    else:
        slow = " (a bit slow)" if ok and rt > tlimit else ""
        txt = f"Correct{slow} in {rt:.1f}s." if ok else f"Not this time — the answer was {answer}."
    return txt + extra


def profile_form():
    st.title("Welcome! Create the child's profile")
    st.info("A few questions to personalise the activities. Use a **first name or nickname** (no surname). "
            "Everything stays on this computer, and you can delete it at any time.")
    name = st.text_input("Child's first name or nickname", key="child_name", max_chars=30)
    age = st.number_input("Age", min_value=3, max_value=99, value=8, key="child_age")
    prof = st.radio("Learning profile (chosen by the parent / guardian)", list(engine.PROFILES),
                    format_func=engine.profile_label, key="child_profile", horizontal=True)
    st.caption("This choice only personalises the activities. The app **never diagnoses, screens or tells anyone** "
               "that a child has a condition, and never guesses it from the answers. It can be changed later.")
    st.caption("Main activity per profile: Typical = brain games · Autism = feelings, friends & routines + my tools · "
               "Dyslexia = reading, writing, word games + build & read · ADHD = focus & self-control games with "
               "movement breaks.")
    sev = "mild"
    if prof != "typical":
        sev = st.radio("Degree / level of support needed (chosen by the parent / guardian)", list(engine.SEVERITIES),
                       format_func=engine.severity_label, key="child_severity", horizontal=True)
        r = engine.SEVERITY_RULES[sev]
        st.caption(f"With this degree: **{r['plan']} questions per series**, practice levels up to **{r['q_cap']}**, "
                   f"brain games up to level **{r['brain_cap']}**, hints **{r['hint']}**. The degree only changes how "
                   "the activities are presented (shorter series, easier start, more help). It is never a diagnosis "
                   "and can be changed later in ⚙ Comfort options.")
    consent = st.checkbox("I am the parent/guardian (or the adult user) and I consent to storing the results on this "
                          f"computer for {engine.RETENTION_DAYS} days, and to processing voice recordings on this "
                          "computer only (they are never saved).", key="child_consent")
    if st.button("Create profile", type="primary"):
        name = name.strip()
        if not name or name == NEW:
            st.error("Please enter a first name or nickname.")
        elif not consent:
            st.error("The parent/guardian (or adult user) must agree to continue.")
        else:
            d = engine.profile_defaults(prof, age, sev)
            engine.set_settings(name, int(age), prof, d["fun"], d["reading"], d["calm"], True, d["focus"], sev)
            ss.active = name
            st.rerun()


# ------------------------------------------------------------- sidebar: who is playing
st.sidebar.title("🧠 Cognitive Growth Agent")
profiles = engine.list_profiles()
options = profiles + [NEW]
if ss.get("active") not in options:
    ss.active = profiles[0] if profiles else NEW
ss.active = st.sidebar.selectbox("Who is playing?", options, index=options.index(ss.active))
st.sidebar.radio("Mode", ["Non-biometric (default)"],
                 help="Typing always works. Voice reading is optional and processed on this computer only.")
if ss.active == NEW:
    profile_form()
    st.stop()

user = ss.active
S = engine.get_settings(user)
age = S["age"] or BAND_AGE[S["age_band"]]
mood_choice = st.sidebar.select_slider("How are you feeling today? (optional, self-reported)",
                                       options=[0, 1, 2, 3, 4, 5],
                                       format_func=lambda x: "skip" if x == 0 else MOODS[x], value=0)
mood = mood_choice or None
voice = st.sidebar.toggle("🔊 Voice coaching (spoken coach answers)", value=False)
modes = [n for n, on in (("Fun", S["fun"]), ("Reading support", S["reading"]), ("Calm", S["calm"]),
                          ("Focus support", S["focus"])) if on]
st.sidebar.caption(f"{user} · age {age} · {engine.profile_label(S['profile'])}"
                   + (f" · {engine.severity_label(S['severity'])}" if S["profile"] != "typical" else "")
                   + (" · " + ", ".join(modes) if modes else ""))
with st.sidebar.expander("⚙ Comfort options"):
    o_fun = st.checkbox("🎮 Fun mode (stars, rounds)", S["fun"], key=f"o_fun_{user}")
    o_read = st.checkbox("📖 Reading support", S["reading"], key=f"o_read_{user}")
    o_calm = st.checkbox("🌿 Calm (no timers, no animations)", S["calm"], key=f"o_calm_{user}")
    o_focus = st.checkbox("⚡ Focus support (short rounds, movement breaks)", S["focus"], key=f"o_focus_{user}")
    o_sev = S["severity"]
    if S["profile"] != "typical":
        o_sev = st.selectbox("Degree / level of support", list(engine.SEVERITIES),
                             index=list(engine.SEVERITIES).index(S["severity"]), format_func=engine.severity_label,
                             key=f"o_sev_{user}")
    if st.button("Save options"):
        engine.set_settings(user, age, S["profile"], o_fun, o_read, o_calm, S["guardian"], o_focus, o_sev)
        st.rerun()
if st.sidebar.button("🗑 Delete this profile and its data"):
    engine.delete_user(user)
    for k in list(ss.keys()):   # forget everything about this child in the session too
        del ss[k]
    st.rerun()
st.sidebar.download_button("⬇ Export this profile's data (JSON)", engine.export_user(user), f"{user}_data.json")

inject_css(S)
R = engine.severity_rules(S["severity"], S["profile"])  # what the degree changes (see engine.SEVERITY_RULES)
cap = min(engine.max_level(S["age_band"]), R["brain_cap"])
ROUND = R["plan"]

profile, hist, df = engine.build_twin(user)
goals = engine.get_goals(user)
plan = engine.make_plan(profile, goals)
beh = engine.behaviour(df)
chat = engine.get_chat(user)
probes = engine.get_probes(user)
df_r = engine.get_reading(user)
df_act = engine.get_activities(user)
df_w = engine.get_writing(user)
rsum = engine.reading_summary(df_r)
wsum = engine.writing_summary(df_w)
psum = engine.practice_summary(df_act)
tricky = literacy.tricky_words(df_w)
practice = {"reading_practice": rsum, "writing_practice": wsum, "tricky_words": tricky[:5],
            "feelings_and_routines_practice": psum.get("social"), "focus_practice": psum.get("focus"),
            "word_games": psum.get("words"),
            "puzzle_and_leaves": psum.get("games"),
            "pauses_taken": int((df_act.domain == "pause").sum()) if len(df_act) else 0}
user_msgs = [m["text"] for m in chat if m["role"] == "user"]
collab_now = collab.score(user_msgs, df, probes)
done_n = sum(p["n"] for p in profile.values())
dims = list(engine.DIMENSIONS)

st.markdown(f"## Hi {user}! 👋")

T_TRAIN, T_READ, T_SOC, T_DASH = "🎯 Brain games", "📖 Reading practice", "🌈 Feelings & routines", "📊 Dashboard"
T_COACH, T_COLLAB, T_VAL, T_ABOUT = "💬 Coach", "🤝 AI Collaboration", "🧪 Validation", "🔒 Ethics & limits"
T_FOCUS, T_WRITE, T_WORDS = "⚡ Focus & self-control", "✍️ Writing practice", "🔤 Word games"
T_PAUSE = "🚀 Pause station"
T_VIS = "🧩 Puzzle & leaves"
T_TOOLS, T_BUILD = "🧰 My tools", "🧱 Build & read"
LITERACY = [T_READ, T_WRITE, T_WORDS, T_BUILD]
main = {"autism": [T_SOC, T_TOOLS, T_VIS], "dyslexia": LITERACY + [T_VIS],
        "adhd": [T_FOCUS, T_VIS]}.get(S["profile"], [])
extra = ([t for t in LITERACY if t not in main] if S["reading"] else []) + \
        ([T_FOCUS] if S["focus"] and T_FOCUS not in main else []) + \
        ([T_VIS] if (S["reading"] or S["focus"] or S["calm"]) and T_VIS not in main else []) + \
        ([T_TOOLS] if S["calm"] and T_TOOLS not in main else [])
labels = main + [T_TRAIN] + extra + [T_PAUSE, T_DASH, T_COACH, T_COLLAB, T_VAL, T_ABOUT]  # pause: every profile
tabs = dict(zip(labels, st.tabs(labels)))
q_cap = min(engine.social_cap(age), R["q_cap"])  # levels 1-2 up to age 7 (or severe degree), then 1-3
C = dict(user=user, S=S, q_cap=q_cap, speak=speak, df_act=df_act, rules=R)
if S["profile"] == "autism" or S["calm"]:
    ui_extra.talk_quick(C)  # the talk board stays available during every activity
ui_extra.talk_banner(C)


# ------------------------------------------------------------- practice questions (autism / ADHD / word games)
def movement_card(key):
    """Movement break (focus support): shown after each short round. Moving is a reward, not a punishment."""
    mv = ss.get(f"{key}_move")
    if not mv:
        return False
    st.success(f"🏃 **Movement break!** {mv}  \nWhen you're done, press the button to come back.")
    if st.button("✅ I'm back!", key=f"{key}_back"):
        ss.pop(f"{key}_move", None)
        st.rerun()
    return True


def plan_line(results, n, label=""):
    """Progress of today's plan: ✅ right answer, ❌ wrong answer, ⬜ not done yet."""
    icons = ["✅" if ok else "❌" for ok in results[:n]] + ["⬜"] * (n - len(results[:n]))
    return "  ➜  ".join(f"{ic} {label}{i + 1}" for i, ic in enumerate(icons))


def practice_tab(key, domain, pick, title, intro, topics, plan_len=None, rounds=False):
    """Shared screen for question-based practice. `rounds`=True: stars + short rounds + movement breaks."""
    plan_len = plan_len or R["plan"]  # questions per series: 5 / 4 / 3 depending on the degree
    st.subheader(title)
    st.caption(intro)
    hist = df_act[df_act.domain == domain].reset_index(drop=True) if len(df_act) else df_act
    done = ss.get(f"{key}_done", 0)
    st.markdown("**Today's plan:** " + plan_line(ss.get(f"{key}_res", []), plan_len)
                + (f"  ·  ⭐ **{ss.get(key + '_stars', 0)}**" if rounds else ""))
    if ss.pop(f"{key}_break", False):
        st.info("☕ Take your time. Come back whenever you are ready — nothing is lost. "
                "You can also visit the 🚀 Pause station tab for a breathing break.")
    if ss.get(f"{key}_msg"):
        ok_, txt = ss[f"{key}_msg"]
        (st.success if ok_ else st.info)(txt)
    if rounds and movement_card(key):
        return
    c1, c2 = st.columns(2)
    topic = c1.selectbox("Topic", ["Mix"] + topics, key=f"{key}_topic")
    if c2.button("☕ I need a break", key=f"{key}_brk"):
        ss.pop(key, None)
        ss[f"{key}_break"] = True
        st.rerun()
    if st.button("▶ Next question", key=f"{key}_next"):
        if rounds and len(ss.get(f"{key}_res", [])) >= plan_len:
            ss[f"{key}_res"] = []  # a new round starts with empty boxes
        recent = ss.get(f"{key}_recent", [])
        it = pick(hist, None if topic == "Mix" else topic, recent)
        ss[f"{key}_recent"] = (recent + [it["id"]])[-300:]
        ss[key] = it
        ss[f"{key}_msg"] = None
        ss[f"{key}_hidden"] = False
        ss[f"{key}_n"] = ss.get(f"{key}_n", 0) + 1
        if it.get("say") and not it.get("memo"):
            speak(it["say"], 0.8)
    it = ss.get(key)
    if not it:
        return
    st.markdown(f"**{it['cat']}** · level {it['level']}" + (f" · {it['tag']}" if it.get("tag") else ""))
    if it.get("memo") and not ss.get(f"{key}_hidden"):
        st.markdown("Read (or listen to) the steps, then hide them and answer the question:")
        st.markdown("<div style='font-size:1.6rem;line-height:2;padding:1rem;border-radius:12px;"
                    "background:rgba(108,92,231,.10)'>" + it["memo"] + "</div>", unsafe_allow_html=True)
        a, b = st.columns(2)
        if a.button("🔊 Listen to the steps", key=f"{key}_memo_say"):
            speak(it["memo"], 0.85)
        if b.button("👀 I've read it — hide it", key=f"{key}_hide"):
            ss[f"{key}_hidden"] = True
            st.rerun()
        return
    st.markdown(f"### {it['q']}")
    if it.get("html"):
        st.markdown(it["html"], unsafe_allow_html=True)
    if it.get("rhythm"):  # sounds are played by the browser (Web Audio), the child can replay them
        components.html(games_content.rhythm_player_html(it["rhythm"]), height=110)
        if it.get("listen_first") and not ss.get(f"{key}_hidden"):
            st.caption("Listen carefully. When you are ready, show the answers (you can still replay it).")
            if st.button("👂 I've listened — show the answers", key=f"{key}_listened"):
                ss[f"{key}_hidden"] = True
                st.rerun()
            return
    if it.get("say") or S["reading"]:
        if st.button("🔊 Listen", key=f"{key}_say"):
            speak(it.get("say") or re.sub(r"[*_~]", "", it["q"]), 0.8)
    n_q = ss.get(key + "_n", 0)
    if it.get("multi"):  # tick several things (e.g. pack the school bag)
        st.markdown("**Tick your answers:**")
        ticked = [c for i, c in enumerate(it["choices"]) if st.checkbox(c, key=f"{key}_cb_{n_q}_{i}")]
        ans = ticked or None
    else:
        ans = st.radio("Pick one", it["choices"], index=None, key=f"{key}_ans_{n_q}")
    if it.get("hint"):
        if R["hint"] == "always shown":
            st.info("💡 " + it["hint"])
        else:
            with st.expander("💡 Need a hint?", expanded=R["hint"] == "offered"):
                st.write(it["hint"])
    if st.button("Check", key=f"{key}_check"):
        if ans is None:
            st.warning("Pick an answer first.")
            return
        if it.get("multi"):
            need, got = set(it["answers"]), set(ans)
            ok = need == got
            missing, extra_ = [x for x in it["answers"] if x not in got], [x for x in ans if x not in need]
        else:
            ok = ans == it["a"] or ans in it.get("accept", [])  # several answers can be right
        engine.log_activity(user, it["cat"], it["id"], it["level"], ok, domain)
        msg = ((it.get("praise") or "Yes!") + " " if ok else "Thanks for trying! ") + it["why"]
        if not ok and it.get("multi"):
            msg += ((" Still to add: " + ", ".join(missing) + ".") if missing else "") + \
                   ((" Not needed: " + ", ".join(extra_) + ".") if extra_ else "")
        elif not ok:
            msg += f" (A good answer: {it['a']})"
        if rounds and ok:
            ss[f"{key}_stars"] = ss.get(f"{key}_stars", 0) + 1
        res = ss.get(f"{key}_res", [])
        if len(res) < plan_len:
            ss[f"{key}_res"] = res + [ok]  # remember right (✅) or wrong (❌) for the plan line
        n_done = done + 1
        if rounds and n_done >= plan_len:
            ss[f"{key}_move"] = focus_content.movement()
            n_done = 0
            msg += "  🎉 Round complete! Time for a movement break."
        elif n_done >= plan_len:
            n_done = plan_len
            msg += "  Today's plan is done. Great work — you can stop here."
        ss[f"{key}_done"] = n_done
        ss[f"{key}_msg"] = (ok, msg)
        ss[key] = None
        st.rerun()


def social_tab():
    theme = engine.kv_get(user, "theme")  # "My interests world" questions use the child's favourite world
    practice_tab("soc", "social", lambda h, c, r: support_content.pick_item(h, q_cap, c, recent=r,
                                                                            ctx={"theme": theme}),
                 "🌈 Feelings, friends & routines",
                 "Short practice questions on feelings, faces, friends, expressions, what others think, routines, "
                 "changes, calming down, the emotion detective, my day in cards, the change detective, "
                 "conversation bubbles, clue puzzles, the solution box, packing my bag and my interests. "
                 "No timer, no ranking, several good answers are accepted, and you can take a break at any time. "
                 "The questions change every time. This is practice, not a test.",
                 support_content.CATEGORIES)


def focus_tab():
    practice_tab("foc", "focus", lambda h, c, r: focus_content.pick_item(h, q_cap, c, recent=r),
                 "⚡ Focus & self-control",
                 "Short games: robot rescue, detective, spot the target, same or different, stop & go, follow the "
                 "steps, treasure map, copy the rhythm, pack your school bag, emotion detective and everyday "
                 f"situations. Rounds of {R['plan']} questions, stars, then a movement break. "
                 "The questions change every time.",
                 focus_content.CATEGORIES, rounds=True)


def words_tab():
    practice_tab("wg", "words", lambda h, c, r: literacy.pick_game(h, q_cap, c, recent=r, tricky=tricky),
                 "🔤 Word games",
                 "Spelling, syllable train, rhyme maze, word order, sound detective, twin words, hidden letters, "
                 "word market, meaning hunt, prefixes & suffixes, story in pictures, copy the rhythm and the "
                 "treasure map. "
                 "Words you found tricky in writing practice come back here ⭐. No timer.",
                 literacy.GAME_CATEGORIES, rounds=S["fun"] and not S["calm"])


# ------------------------------------------------------------- puzzle & hidden leaves (autism, ADHD, dyslexia)
def _finish_visual(game, label):
    """Log a finished puzzle / leaves game once (success adapts the next level)."""
    if game["done"] and not game["logged"]:
        game["logged"] = True
        ok = visual_games.puzzle_success(game) if game["kind"] == "puzzle" else visual_games.leaves_success(game)
        engine.log_activity(user, label, game["id"], game["level"], ok, "games")
        if S["fun"] and not S["calm"]:
            st.balloons()


def puzzle_ui(hist):
    h = hist[hist.category == "Puzzle"] if len(hist) else hist
    if st.button("▶ New puzzle", key="pz_new"):
        ss.pz = visual_games.new_puzzle(level_from_history(h, q_cap))
    pz = ss.get("pz")
    if not pz:
        st.info("Press **New puzzle** to start. A new picture is drawn every time.")
        return
    n = len(pz["tiles"])
    st.caption(f"Level {pz['level']} · {n} pieces · pieces in the wrong place tried: {pz['mistakes']}")
    if pz["msg"]:
        (st.success if pz["msg"][0] else st.info)(pz["msg"][1])
    if pz["level"] == 2 and not pz["done"]:
        st.image(pz["model"], caption="The model", width=240)
    if pz["level"] == 3 and not pz["done"] and st.button("👀 Peek at the picture", key="pz_peek"):
        pz["peeks"] += 1
        st.image(pz["model"], caption="The model", width=240)
    if not pz["done"]:
        st.markdown("**1.** Press **✋ Take** under a piece.  **2.** Press **📍 Here** where it goes on the board.")
    st.markdown("**The board**")
    for r in range(pz["rows"]):
        cols = st.columns(pz["cols"], gap="small")
        for c in range(pz["cols"]):
            slot = r * pz["cols"] + c
            with cols[c]:
                if slot in pz["placed"]:
                    st.image(pz["tiles"][pz["placed"][slot]])
                else:
                    st.image(pz["ghosts"][slot])
                    if pz["selected"] is not None and st.button("📍 Here", key=f"pz_put_{slot}"):
                        visual_games.puzzle_put(pz, slot)
                        st.rerun()
    if pz["tray"]:
        st.markdown("**Your pieces**")
        tray = pz["tray"]
        for start in range(0, len(tray), pz["cols"]):
            cols = st.columns(pz["cols"], gap="small")
            for col, p in zip(cols, tray[start:start + pz["cols"]]):
                with col:
                    st.image(pz["tiles"][p])
                    taken = pz["selected"] == p
                    if st.button("✅ Taken" if taken else "✋ Take", key=f"pz_take_{p}",
                                 type="primary" if taken else "secondary"):
                        visual_games.puzzle_take(pz, p)
                        st.rerun()
    _finish_visual(pz, "Puzzle")


def leaves_ui(hist):
    h = hist[hist.category == "Leaves"] if len(hist) else hist
    if st.button("▶ New leaves game", key="lv_new"):
        ss.lv = visual_games.new_leaves(level_from_history(h, q_cap))
    m = ss.get("lv")
    if not m:
        st.info("Press **New leaves game** to start. The leaves change every time.")
        return
    st.caption(f"Level {m['level']} · tries: {m['tries']}")
    tips = {"find": "Find the **two leaves that are exactly the same** (same shape AND same colour). "
                    "Press 👆 under a leaf to pick it.",
            "look": "Look at all the leaves and **remember where they are**. When you are ready, hide them.",
            "play": "Turn over **two cards**. If they are the same, they stay up ✅. Find all the pairs!"}
    st.markdown(tips[m["phase"]])
    if m["msg"]:
        (st.success if m["msg"][0] else st.info)(m["msg"][1])
    if m["phase"] == "look" and st.button("🙈 I'm ready — hide the cards", key="lv_hide"):
        m["phase"] = "play"
        st.rerun()
    if m["phase"] == "play" and len(m["up"]) == 2 and st.button("🙈 Turn them back", key="lv_back"):
        m["up"] = []
        m["msg"] = None
        st.rerun()
    per_row = 4
    for start in range(0, len(m["cards"]), per_row):
        cols = st.columns(per_row)
        for col, i in zip(cols, range(start, min(start + per_row, len(m["cards"])))):
            with col:
                if i in m["matched"]:
                    state = "match"
                elif m["phase"] == "find":
                    state = "pick" if i in m["up"] else "up"
                else:
                    state = "up" if m["phase"] == "look" or i in m["up"] else "down"
                st.markdown(visual_games.card_html(i + 1, m["cards"][i], state), unsafe_allow_html=True)
                if not m["done"] and m["phase"] != "look" and i not in m["matched"] and i not in m["up"]:
                    if st.button("👆 Pick" if m["phase"] == "find" else "🔄 Turn", key=f"lv_{i}"):
                        visual_games.leaves_flip(m, i)
                        st.rerun()
    _finish_visual(m, "Leaves")


def visual_tab():
    st.subheader("🧩 Puzzle & hidden leaves")
    st.caption("Picture games: no reading, no timer. The level adapts to the last games, and a new picture or a "
               "new set of leaves is made every time.")
    hist = df_act[df_act.domain == "games"].reset_index(drop=True) if len(df_act) else df_act
    game = st.radio("Choose a game", ["🧩 Puzzle", "🍂 Find the same leaves"], horizontal=True, key="vg_game")
    if game.startswith("🧩"):
        puzzle_ui(hist)
    else:
        leaves_ui(hist)


# ------------------------------------------------------------- space pause station (every profile)
def pause_tab():
    st.subheader("🚀 Space pause station")
    st.caption("Between two games, take a short pause. You choose how long, and you can stop whenever you want. "
               "Nothing is scored here.")
    n_p = int((df_act.domain == "pause").sum()) if len(df_act) else 0
    lvl = games_content.pause_level(n_p)
    kinds = list(games_content.PAUSE_KINDS)[:lvl]  # more choices appear after a few pauses
    if ss.get("ps_msg"):
        st.success(ss.ps_msg)
    kind = st.radio("What kind of pause?", kinds, format_func=games_content.PAUSE_KINDS.get, key="ps_kind",
                    horizontal=True) if len(kinds) > 1 else kinds[0]
    if len(kinds) == 1:
        st.markdown("**⭐ Breathe with the star:** follow the star as it grows (breathe in) and shrinks (breathe out).")
    idea = st.radio("Choose your pause idea", games_content.OWN_IDEAS, key="ps_idea") if kind == "own" else ""
    secs = st.select_slider("How long?", [20, 30, 45, 60], value=20, key="ps_secs",
                            format_func=lambda x: f"{x} seconds")
    if st.button("▶ Start my pause", key="ps_start", type="primary"):
        ss.ps_on = ss.get("ps_on", 0) + 1
        ss.ps_msg = None
        engine.log_activity(user, games_content.PAUSE_KINDS[kind], secs, lvl, True, "pause")
        st.rerun()
    if ss.get("ps_on"):
        components.html(games_content.pause_html(kind, secs, idea), height=290)
        a, b = st.columns(2)
        if a.button("✅ I'm ready to continue", key="ps_done"):
            ss.ps_on = 0
            ss.ps_msg = "You took a moment for yourself. 🌟 Do you want to continue playing or take another pause?"
            st.rerun()
        if b.button("🔁 Another pause", key="ps_again"):
            ss.ps_on += 1
            engine.log_activity(user, games_content.PAUSE_KINDS[kind], secs, lvl, True, "pause")
            st.rerun()
    st.caption(f"Pauses taken: {n_p}. " + ("More pause choices appear after a few pauses." if lvl < 3 else ""))


# ------------------------------------------------------------- writing practice (look, hide, write)
def writing_tab():
    st.subheader("✍️ Look, hide, write")
    st.write("**1.** Look at the sentence (you can listen to it).  **2.** Hide it and write it from memory.  "
             "**3.** The agent checks every word and every letter, shows what to fix, and you try again. No timer.")
    mode = st.radio("How do you want to practise?", list(literacy.MODES), format_func=literacy.MODES.get,
                    horizontal=True, key="wr_mode")
    if st.button("▶ New writing sentence", key="wr_new"):
        lvl = literacy.writing_level(df_w, cap)
        used = df_w[df_w.attempt == 1].text_id.tolist() if len(df_w) else []
        tid, text = literacy.pick_writing(lvl, used)
        ss.wr_n = ss.get("wr_n", 0) + 1
        ss.wr = dict(id=tid, level=lvl, text=text, mode=mode, attempt=1,
                     phase="look" if mode == "look" else "write", res1=None, res2=None, spoken=False)
        if mode == "listen":
            speak(text, 0.8)
    wr = ss.get("wr")
    if not wr:
        return

    def sentence_box():
        st.markdown("<div style='font-size:1.7rem;line-height:2.1;letter-spacing:.05em;padding:1rem;"
                    "border-radius:12px;background:rgba(108,92,231,.10)'>" + wr["text"] + "</div>",
                    unsafe_allow_html=True)

    st.caption(f"Level {wr['level']}/5 · {literacy.MODES[wr['mode']]}" + (" · second try" if wr["attempt"] == 2 else ""))
    ph = wr["phase"]
    if ph == "look":
        st.markdown("Look carefully at each word. When you are ready, hide it and write it.")
        sentence_box()
        a, b = st.columns(2)
        if a.button("🔊 Listen", key="wr_listen_look"):
            speak(wr["text"], 0.8)
        if b.button("✅ I'm ready — hide it", key="wr_hide"):
            wr["phase"] = "write"
            st.rerun()
    elif ph == "write":
        if wr["mode"] == "copy":
            sentence_box()
        elif wr["mode"] == "listen":
            st.info("🎧 Listen to the sentence, then write it. You can listen as many times as you need.")
        else:
            st.info("🙈 The sentence is hidden. Write it from memory!")
        if wr["mode"] != "look" and st.button("🔊 Listen", key=f"wr_listen_{wr['attempt']}"):
            speak(wr["text"], 0.8)
        typed = st.text_area("Write the sentence here", key=f"wr_{ss.wr_n}_{wr['attempt']}", height=90)
        if st.button("✔ Check my writing", key="wr_check"):
            if not typed.strip():
                st.warning("Write the sentence first.")
                return
            res = literacy.compare_writing(wr["text"], typed)
            engine.log_writing(user, wr["id"], wr["level"], wr["mode"], wr["attempt"], res)
            wr[f"res{wr['attempt']}"] = res
            perfect = res["n_wrong"] == 0 and not res["extra"]
            wr["phase"] = "done" if perfect or wr["attempt"] == 2 else "feedback"
            st.rerun()
    elif ph == "feedback":
        res = wr["res1"]
        st.markdown(literacy.marks_html(res), unsafe_allow_html=True)
        st.info(literacy.writing_feedback(res))
        for tip in res["tips"]:
            st.markdown("💡 " + tip)
        st.markdown("**The right sentence:**")
        sentence_box()
        script = literacy.writing_script(user, wr["text"], res)
        if not wr["spoken"]:
            wr["spoken"] = True
            speak(script, 0.8)
        a, b = st.columns(2)
        if a.button("🔊 Listen to the tricky words", key="wr_script"):
            speak(script, 0.8)
        if b.button("✏️ Write it again", key="wr_again"):
            wr["attempt"] = 2
            wr["phase"] = "look" if wr["mode"] == "look" else "write"
            st.rerun()
    else:  # done
        r1, r2 = wr["res1"], wr["res2"]
        last = r2 or r1
        st.markdown(literacy.marks_html(last), unsafe_allow_html=True)
        if r2 is None:
            st.success("Perfect on the first try! Every word is spelled correctly. 🌟")
        elif (r2["word_acc"], r2["letter_acc"]) > (r1["word_acc"], r1["letter_acc"]):
            st.success(f"First try {r1['word_acc'] * 100:.0f}% → second try {r2['word_acc'] * 100:.0f}% of the words "
                       "spelled correctly: you improved! 🌟")
        else:
            st.info(f"First try {r1['word_acc'] * 100:.0f}% → second try {r2['word_acc'] * 100:.0f}%. "
                    "Every try helps you learn.")
        if r2 is not None and r2["n_wrong"]:
            st.markdown("**The right sentence:**")
            sentence_box()
        note = literacy.writing_feedback(last)
        if "reminder" in note:
            st.caption(note[note.index("Small reminder"):])
        if S["fun"] and not S["calm"] and not wr.get("shown"):
            wr["shown"] = True
            st.balloons()
        st.caption("Press **New writing sentence** for the next one. Misspelled words come back in 🔤 Word games.")


# ------------------------------------------------------------- reading practice
def voice_box(rd, tag):
    """Read aloud: record -> local transcription -> the parent can fix the transcript before checking."""
    key = f"{ss.rd_n}_{tag}"
    audio = st.audio_input("🎤 Read the sentence aloud", key=f"aud_{key}")
    if audio is not None and rd.get("heard_key") != key:
        with st.spinner("Listening..."):
            text, err = stt.transcribe(audio.getvalue())
        rd.update(heard_key=key, heard=text, err=err)
    if rd.get("heard_key") == key:
        if rd.get("err"):
            st.error("Voice detection is not available right now (" + rd["err"][:120] + "). "
                     "You can type what was read in the box below.")
        elif not rd["heard"]:
            st.warning("We could not hear anything. Try recording again, or type it below.")
        return st.text_area("What we heard (a parent can fix it before checking)", value=rd["heard"],
                            key=f"heard_{key}")
    return None


def reading_tab():
    st.subheader("📖 Read, listen, fix")
    st.write("**1.** Read the sentence (you can listen to it first).  **2.** The agent checks your reading.  "
             "**3.** If a word needs polishing, the voice reads it correctly, and you try again. No timer.")
    voice_ok = hasattr(st, "audio_input") and stt.available()
    opts = (["🎤 Read aloud (voice)"] if voice_ok else []) + ["⌨️ Type it (no microphone)"]
    if not voice_ok:
        st.caption("Voice reading needs the optional voice package (`pip install faster-whisper`, see README). "
                   "Typing works without it.")
    mode_sel = st.radio("How do you want to show your reading?", opts, horizontal=True)
    if st.button("▶ New sentence", key="rd_new"):
        lvl = engine.reading_level(df_r, cap)
        used = df_r[df_r.attempt == 1].text_id.tolist() if len(df_r) else []
        tid, text = engine.pick_text(lvl, used)
        ss.rd_n = ss.get("rd_n", 0) + 1
        ss.rd = dict(phase="read", id=tid, level=lvl, text=text, acc1=None, acc2=None, marks=None, msg="",
                     mode="voice" if mode_sel.startswith("🎤") else "typed")
    rd = ss.get("rd")
    if not rd:
        return
    is_voice = rd["mode"] == "voice"

    def check(typed, attempt):
        if not typed.strip():
            st.warning("Nothing to check yet.")
            return
        res = engine.compare_reading(rd["text"], typed, 0.8 if is_voice else 1.0)
        engine.log_reading(user, rd["id"], rd["level"], attempt, res["accuracy"], res["n_words"], res["n_wrong"])
        rd["marks"], rd["msg"] = res["marks"], engine.reading_feedback(res)
        rd["script"] = engine.correction_script(user, rd["text"], res["marks"])
        if attempt == 1:
            rd["acc1"] = res["accuracy"]
            rd["phase"] = "done" if res["n_wrong"] == 0 else "feedback"
        else:
            rd["acc2"] = res["accuracy"]
            rd["phase"] = "done"
        st.rerun()

    st.caption(f"Level {rd['level']}/5")
    ph = rd["phase"]
    if ph == "read":
        st.markdown("<div style='font-size:1.7rem;line-height:2.1;letter-spacing:.05em;padding:1rem;"
                    "border-radius:12px;background:rgba(108,92,231,.10)'>" + rd["text"] + "</div>",
                    unsafe_allow_html=True)
        if st.button("🔊 Listen first"):
            speak(rd["text"], 0.85)
        if is_voice:
            typed = voice_box(rd, "1")
            if typed is not None and st.button("Check my reading"):
                check(typed, 1)
        elif st.button("✅ I'm ready — hide it"):
            rd["phase"] = "write"
            st.rerun()
    elif ph == "write":
        typed = st.text_input("Type the sentence you read", key=f"rd_{ss.rd_n}_write")
        if st.button("Check", key="rd_check1"):
            check(typed, 1)
    elif ph == "feedback":
        st.markdown(marks_html(rd["marks"]), unsafe_allow_html=True)
        st.info(rd["msg"])
        if not rd.get("spoken"):  # the voice agent reads the correct sentence, then the tricky words
            rd["spoken"] = True
            speak(rd["script"], 0.8)
        c1, c2 = st.columns(2)
        if c1.button("🔊 Listen to the correct reading"):
            speak(rd["script"], 0.8)
        if c2.button("✏️ Try again"):
            rd["phase"] = "retry"
            st.rerun()
    elif ph == "retry":
        st.markdown("Look at the highlighted words, then read the whole sentence again:")
        st.markdown(marks_html(rd["marks"]), unsafe_allow_html=True)
        if st.button("🔊 Listen again"):
            speak(rd["script"], 0.8)
        if is_voice:
            typed = voice_box(rd, "2")
            if typed is not None and st.button("Check my reading"):
                check(typed, 2)
        else:
            typed = st.text_input("Type the sentence again", key=f"rd_{ss.rd_n}_retry")
            if st.button("Check", key="rd_check2"):
                check(typed, 2)
    else:  # done
        st.markdown(marks_html(rd["marks"]), unsafe_allow_html=True)
        a1, a2 = rd["acc1"], rd["acc2"]
        if a2 is None:
            st.success("Perfect on the first try! 🌟")
            if not rd.get("spoken"):
                rd["spoken"] = True
                speak(f"Well read, {user}!", 0.9)
        elif a2 > a1:
            st.success(f"First try {a1 * 100:.0f}% → second try {a2 * 100:.0f}%: you improved! 🌟")
        else:
            st.info(f"First try {a1 * 100:.0f}% → second try {a2 * 100:.0f}%. Every try helps you learn.")
        if S["fun"] and not S["calm"] and not rd.get("shown"):
            rd["shown"] = True
            st.balloons()
        st.caption("Press **New sentence** for the next one.")


for _label, _fn in ((T_SOC, social_tab), (T_FOCUS, focus_tab), (T_READ, reading_tab), (T_WRITE, writing_tab),
                    (T_WORDS, words_tab), (T_PAUSE, pause_tab), (T_VIS, visual_tab),
                    (T_TOOLS, lambda: ui_extra.tools_tab(C)), (T_BUILD, lambda: ui_extra.build_tab(C))):
    if _label in tabs:
        with tabs[_label]:
            _fn()

# ------------------------------------------------------------- A: train (brain games)
with tabs[T_TRAIN]:
    unit = "game" if S["fun"] else "exercise"
    st.subheader("Let's play! 🎮" if S["fun"] else "Adaptive exercises")
    if ss.pop("celebrate", False) and S["fun"] and not S["calm"]:
        st.balloons()
    movement_card("bg")
    if S["fun"]:
        st.markdown(f"⭐ **Stars: {ss.get('stars', 0)}**")
        st.progress(ss.get("round_n", 0) / ROUND, text=f"Round: {ss.get('round_n', 0)}/{ROUND}")
    if S["calm"]:
        st.markdown("**Today's plan:** " + plan_line(ss.get("calm_res", []), 3, "Step ")
                    + " — you can stop at any time.")
    if done_n < engine.CALIBRATION_TRIALS:
        st.progress(done_n / engine.CALIBRATION_TRIALS,
                    text=f"Calibration: {done_n}/{engine.CALIBRATION_TRIALS} {unit}s "
                         "(we first estimate every dimension)")
    with st.expander("How it works", expanded=(done_n == 0)):
        st.markdown(f"1. Press **New {unit}** and answer. 2. Your **Brain Twin** updates (estimate + range). "
                    "3. The next one is chosen to be challenging but fair, and **we tell you why**. "
                    "4. Ask your **Coach** anything. Nothing here is a medical or clinical test.")
    top = plan[0]
    st.info(f"Recommended next: **{top['dim']}** at level {min(top['level'], cap)}/5 — {top['reason']}.")
    choice = st.selectbox("Dimension", ["Auto (recommended)"] + dims)

    if st.button(f"▶ New {unit}"):
        old = ss.get("trial")
        if old:  # unanswered = abandoned (behaviour signal, does not change the estimate)
            engine.log_trial(user, old, False, 0.0, ss.get("hint", False), ss.get("changes", 0),
                             ss.get("t_first"), mood, abandoned=True)
        if choice.startswith("Auto"):
            dim = engine.pick_dimension(profile, plan)
            mode = "calibration" if done_n < engine.CALIBRATION_TRIALS else "priority"
        else:
            dim, mode = choice, "manual"
        level = min(engine.next_level(profile[dim]["mean"]), cap)
        low_mood = mood is not None and mood <= 2 and level > 1
        if low_mood:
            level -= 1
        t = engine.make_trial(dim, level, avoid=ss.get("recent_sigs", []))
        ss.recent_sigs = (ss.get("recent_sigs", []) + [t["sig"]])[-60:]  # no repeat of the last 60 exercises
        if S["calm"]:
            t["tlimit"] = 999.0           # no time pressure: slowness never lowers the estimate
            t["show_s"] = t["show_s"] * 1.5
        t["why"] = engine.explain_trial(dim, level, profile, goals, mode, low_mood)
        ss.update(trial=t, tid=uuid.uuid4().hex, hint=False, feedback=None, changes=0,
                  first_done=False, t_first=None, t0=None if t["memorize"] else time.time())

    if ss.get("feedback"):
        ok, msg = ss.feedback
        (st.success if ok else st.error)(msg)

    t = ss.get("trial")
    if t:
        st.markdown(f"**{t['dim']} — level {t['level']}/5**  \n*{engine.DIMENSIONS[t['dim']]}*")
        st.caption("🧭 Why this one? " + t["why"])
        if t["memorize"] and ss.t0 is None:
            if st.button("👁 Show the sequence (it disappears quickly)"):
                ph = st.empty()
                ph.markdown(f"# {t['memorize']}")
                time.sleep(t["show_s"])
                ph.empty()
                ss.t0 = time.time()
                st.rerun()
        else:
            st.write(t["prompt"])
            if S["reading"] and st.button("🔊 Listen to the question"):
                speak(t["prompt"], 0.9)
            if t["html"]:
                st.markdown(t["html"], unsafe_allow_html=True)
            ans = st.radio("Your answer", t["choices"], index=None, key="r" + ss.tid, on_change=on_answer)
            c1, c2 = st.columns(2)
            if c2.button("💡 Hint"):
                ss.hint = True
            if ss.hint or R["hint"] == "always shown":
                st.caption("Hint: " + t["hint"])
            if c1.button("Submit", type="primary"):
                if ans is None:
                    st.warning("Choose an answer first.")
                else:
                    rt = time.time() - ss.t0
                    ok = ans == t["answer"]
                    engine.log_trial(user, t, ok, rt, ss.hint, ss.get("changes", 0), ss.get("t_first"), mood)
                    extra = ""
                    if ok:
                        ss.stars = ss.get("stars", 0) + 1
                    if S["fun"]:
                        ss.round_n = ss.get("round_n", 0) + 1
                        if ss.round_n >= ROUND:
                            ss.round_n = 0
                            ss.celebrate = True
                            extra = " 🎉 Round complete!"
                            if S["focus"]:
                                ss.bg_move = focus_content.movement()
                                extra += " Time for a movement break!"
                    if S["calm"]:
                        ss.calm_done = min(3, ss.get("calm_done", 0) + 1)
                        if len(ss.get("calm_res", [])) < 3:
                            ss.calm_res = ss.get("calm_res", []) + [ok]
                        if ss.calm_done >= 3:
                            extra = " Today's plan is done. Great work — you can stop here."
                    ss.feedback = (ok, feedback_text(ok, t["answer"], rt, t["tlimit"], S, extra))
                    ss.trial = None
                    st.rerun()

# ------------------------------------------------------------- C: dashboard
with tabs[T_DASH]:
    st.subheader("Your Brain Twin (estimates with 95% uncertainty range)")
    table = pd.DataFrame([{"Dimension": d, "Estimate %": round(profile[d]["mean"]),
                           "Range %": f"{profile[d]['lo']:.0f}–{profile[d]['hi']:.0f}",
                           "Exercises": profile[d]["n"],
                           "Reliability": "rough" if profile[d]["n"] < 5 else "fair"} for d in dims])
    st.dataframe(table, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for key, name, dash, fill in (("hi", "upper range", "dot", None), ("mean", "estimate", "solid", "toself"),
                                      ("lo", "lower range", "dot", None)):
            r = [profile[d][key] for d in dims]
            fig.add_trace(go.Scatterpolar(r=r + r[:1], theta=dims + dims[:1], name=name,
                                          line=dict(dash=dash), fill=fill))
        fig.update_layout(title="Radar profile", polar=dict(radialaxis=dict(range=[0, 100])))
        st.plotly_chart(fig)
    with c2:
        if len(hist):
            st.plotly_chart(px.line(hist, x="attempt", y="mean", color="dim", title="Progress curves",
                                    labels={"mean": "estimate %", "attempt": "exercise #"}))
        else:
            st.info("Do a few exercises to see your progress curves.")

    if len(df):
        ok_df = df[df.abandoned.fillna(0) == 0]
        piv = (ok_df.groupby(["dim", "level"]).correct.mean().unstack()
               .reindex(index=dims, columns=range(1, engine.LEVELS + 1)))
        st.plotly_chart(px.imshow(piv, text_auto=".0%", color_continuous_scale="Blues", zmin=0, zmax=1,
                                  aspect="auto", title="Heatmap: success rate by dimension and level"))

    if len(df_r):
        st.subheader("Reading practice")
        rr = df_r.reset_index(drop=True).assign(step=lambda x: x.index + 1,
                                                attempt=lambda x: "try " + x.attempt.astype(str))
        st.plotly_chart(px.line(rr, x="step", y="accuracy", color="attempt", markers=True,
                                title="Words read correctly (first vs second try)", range_y=[0, 1.05]))
        if rsum:
            st.caption(f"{rsum['sentences']} sentences · first try ≈ {rsum['first_try_accuracy']}%"
                       + (f" · second try ≈ {rsum['second_try_accuracy']}%"
                          if rsum["second_try_accuracy"] is not None else ""))

    if len(df_w):
        st.subheader("Writing practice (look, hide, write)")
        ww = df_w.reset_index(drop=True).assign(step=lambda x: x.index + 1,
                                                attempt=lambda x: "try " + x.attempt.astype(str))
        st.plotly_chart(px.line(ww, x="step", y="word_acc", color="attempt", markers=True, range_y=[0, 1.05],
                                title="Words written correctly (first vs second try)",
                                labels={"word_acc": "words correct"}))
        if wsum:
            st.caption(f"{wsum['sentences']} sentences · first try ≈ {wsum['first_try_words_correct']}% of words"
                       + (f" · second try ≈ {wsum['second_try_words_correct']}%"
                          if wsum["second_try_words_correct"] is not None else ""))
        if tricky:
            st.markdown("**Tricky words to practise:** " + ", ".join(f"`{w}`" for w in tricky)
                        + "  (they come back in 🔤 Word games)")

    for dom, title in (("social", "Feelings, friends & routines"), ("focus", "Focus & self-control"),
                       ("words", "Word games"), ("games", "Puzzle & leaves")):
        if psum.get(dom):
            st.subheader(title)
            d = psum[dom]
            st.plotly_chart(px.bar(x=list(d), y=list(d.values()), labels={"x": "topic", "y": "answered well %"},
                                   range_y=[0, 100], title=f"{title}: questions answered well"),
                            key=f"bar_{dom}")
    if psum.get("checkin"):
        last = df_act[df_act.domain == "checkin"].category.iloc[-1]
        st.caption(f"🎯 Emotion radar check-ins: {int((df_act.domain == 'checkin').sum())} (last: {last}). "
                   "Self-reported by the child; never interpreted.")
    if psum.get("tools"):
        st.caption("🧰 Tools used: " + ", ".join(f"{k} ×{int(((df_act.domain == 'tools') & (df_act.category == k)).sum())}"
                                                  for k in psum["tools"]))
    if psum.get("pause"):
        st.caption(f"🚀 Pauses taken in the pause station: {int((df_act.domain == 'pause').sum())} "
                   "(taking a pause is a good skill, not a problem).")
    if psum:
        st.caption("Practice progress only: it is not a screening and says nothing about the child's health.")

    st.subheader("Behaviour signals (from your interactions only)")
    if beh and beh["n"]:
        m = st.columns(5)
        m[0].metric("Hints used", f"{beh['hint_rate'] * 100:.0f}%")
        m[1].metric("Answer changes / exercise", f"{beh['avg_answer_changes']:.2f}")
        m[2].metric("Time before 1st choice", "n/a" if beh["hesitation"] is None else f"{beh['hesitation'] * 100:.0f}%")
        m[3].metric("Speed vs limit", f"{beh['speed_ratio'] * 100:.0f}%", help="Below 100% = within the time limit")
        m[4].metric("Abandoned", f"{beh['abandon_rate'] * 100:.0f}%")
    else:
        st.info("Behaviour signals appear after a few exercises.")

    st.subheader("Optional projection (a scenario, not a promise)")
    pdim = st.selectbox("Dimension to project", dims, key="pdim")
    proj = engine.project(hist[hist.dim == pdim]) if len(hist) else None
    if proj is None:
        st.info("Not enough exercises yet to project (at least 8 in this dimension).")
    else:
        h = hist[hist.dim == pdim]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=h.attempt, y=h["mean"], name="estimate so far"))
        fig.add_trace(go.Scatter(x=proj.attempt, y=proj.hi, line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=proj.attempt, y=proj.lo, fill="tonexty", line=dict(width=0),
                                 name="plausible range"))
        fig.add_trace(go.Scatter(x=proj.attempt, y=proj["mean"], line=dict(dash="dash"), name="projection"))
        fig.update_layout(yaxis=dict(range=[0, 100]), xaxis_title="exercise #", yaxis_title="estimate %")
        st.plotly_chart(fig)
        st.caption("Assumes you keep training at the same rhythm. The trend is deliberately shrunk by 50% and the "
                   "band widens with distance: the future is uncertain.")

    st.subheader("Goals")
    for d in dims:
        g = st.slider(f"Goal — {d}", 10, 100, int(goals[d]), 5, key=f"g_{user}_{d}")
        if g != goals[d]:
            engine.set_goal(user, d, g)
        p = profile[d]
        st.progress(min(p["mean"] / g, 1.0),
                    text=f"{p['mean']:.0f}% now (range {p['lo']:.0f}–{p['hi']:.0f}) → goal {g}%")

    st.subheader("Learning plan (updated after every exercise)")
    st.dataframe(pd.DataFrame(plan)[["dim", "level", "n_trials", "gap", "reason"]]
                 .rename(columns={"dim": "Focus", "level": "Level", "n_trials": "Exercises",
                                  "gap": "Gap to goal", "reason": "Why"}), hide_index=True)

# ------------------------------------------------------------- B: coach
with tabs[T_COACH]:
    st.subheader("Your explainable coach")
    for m in chat:
        st.chat_message(m["role"]).write(m["text"])
    if voice and chat:
        last = [m for m in chat if m["role"] == "assistant"]
        if last and st.button("🔊 Read the last answer aloud"):
            speak(last[-1]["text"])
    if not chat and st.button("Get my first summary"):
        engine.log_chat(user, "assistant", coach.reply(profile, plan, collab_now, [], None, beh, mood, S, practice))
        st.rerun()
    msg = st.chat_input("Ask your coach (e.g. 'Why should I train attention?')")
    if msg:
        engine.log_chat(user, "user", msg)
        chat = engine.get_chat(user)
        cnow = collab.score([m["text"] for m in chat if m["role"] == "user"], df, probes)
        engine.log_chat(user, "assistant", coach.reply(profile, plan, cnow, chat, msg, beh, mood, S, practice))
        st.rerun()

# ------------------------------------------------------------- AI collaboration score
with tabs[T_COLLAB]:
    st.subheader("AI Collaboration Score")
    st.metric("Score (0–100)", collab_now["score"])
    st.caption(f"Messages analysed: {collab_now['n_msgs']} — challenges done: {collab_now['n_probes']} — "
               f"confidence: {collab_now['confidence']}")
    st.bar_chart(pd.Series(collab_now["components"]))
    st.caption("Critical verification: " + collab_now["verification_source"])
    st.markdown("**Formula (unvalidated design proposal):** "
                + " + ".join(f"{w:.2f}×{k}" for k, w in collab.WEIGHTS.items()))

    st.subheader("🔎 Spot-the-error challenge")
    st.write("The coach states something about **your own profile**. Sometimes it is wrong on purpose. "
             "Do you check before trusting it?")
    if st.button("New challenge"):
        ss.probe = engine.make_probe(profile)
        ss.verified = False
        ss.pfeedback = None
        if ss.probe is None:
            st.info("Do exercises in at least 2 dimensions first.")
    if ss.get("pfeedback"):
        st.info(ss.pfeedback)
    probe = ss.get("probe")
    if probe:
        st.warning(f"🤖 Coach says: **{probe['claim']}**")
        if st.button("🔍 Verify first (show my data)"):
            ss.verified = True
        if ss.get("verified"):
            st.dataframe(table[["Dimension", "Estimate %", "Range %", "Exercises"]], hide_index=True)
        a, b = st.columns(2)
        action = "accept" if a.button("✅ Accept") else ("flag" if b.button("❌ This is wrong") else None)
        if action:
            sc = engine.log_probe(user, probe, action, ss.get("verified", False))
            truth = "was WRONG on purpose" if probe["flawed"] else "was correct"
            ss.pfeedback = (f"The claim {truth}. Your verification score for this challenge: {sc:.1f}/1. "
                            + ("Well done." if sc >= 0.8 else "Tip: compare with your dashboard before deciding."))
            ss.probe = None
            st.rerun()

# ------------------------------------------------------------- validation
with tabs[T_VAL]:
    st.subheader("Does the Brain Twin recover the true level?")
    st.markdown("We simulate **virtual users with a known skill** and check (1) the estimation error, "
                "(2) whether the 95% interval really contains the truth, and (3) robustness to guessing, "
                "slow or hint-heavy behaviour. 'Mismatched' users do **not** follow the estimator's own model.")
    if st.button("Run quick simulation (~20 s)"):
        with st.spinner("Simulating virtual users..."):
            import simulate
            res = simulate.run(quick=True)
            ss.sim = (simulate.summarize(res), simulate.make_figure(res))
    if ss.get("sim"):
        summ, fig = ss.sim
        st.pyplot(fig)
        st.dataframe(summ["accuracy"][summ["accuracy"].n == 40], hide_index=True)
        st.dataframe(summ["robustness"], hide_index=True)
    elif Path("validation/validation.png").exists():
        st.image("validation/validation.png")
        st.markdown(Path("validation/summary.md").read_text(encoding="utf-8"))
    else:
        st.info("Run the simulation here, or `python simulate.py` for the full report.")

# ------------------------------------------------------------- ethics
with tabs[T_ABOUT]:
    st.markdown(f"""
### What this app is, and is not
A learning and practice tool. It is **not a medical device, not a screening and not a therapy**. It never diagnoses,
never tells anyone that a child has (or has not) a condition, and never guesses it from the answers.
The coach output is filtered for clinical vocabulary. For any concern about a child's development or learning,
please talk to a qualified professional.

### The profile
The parent/guardian chooses a profile (typical, autism, dyslexia, ADHD) **only to personalise the activities**:
reading practice with voice feedback, look-hide-write and dictation with letter-by-letter correction, word games,
practice questions on feelings, friends and routines, focus games with short rounds and movement breaks, calm pacing.
It can be changed or deleted at any time. Under the hood it is just a setting: no result is ever
interpreted as a sign of any condition. Use a first name or nickname only.

### Data and voice
- **Consent** by the parent/guardian (or the adult user) before anything is stored. **Local** SQLite file only.
- **Retention:** automatic deletion of exercise, chat, reading and practice data after {engine.RETENTION_DAYS} days.
  **Deletion:** sidebar button. **Export:** JSON.
- **Voice (optional):** the recording is processed **in memory, on this computer**, by a local model
  and is **never saved or sent anywhere**; only the transcript (editable by a parent) and the accuracy are kept.
  Typing always works, so a non-biometric mode is always available. Nothing is decided from the voice alone.
- No camera. Mood is self-reported and optional.

### Limits and bias
- Speech recognition is less accurate on children's voices and accents: it can mistake its own errors for the
  child's. That is why near-matches are accepted for voice and a parent can correct the transcript.
- Reading practice measures accuracy on short English sentences, not reading ability in general.
- The practice questions are original, short and simple; they are not validated by specialists and make no
  therapeutic claim. Social situations are presented as options, never as a single "right way to be".
- Questions are generated or rotated so they rarely repeat; a generated question can occasionally be imperfect
  (e.g. a distractor that is also a real word). Writing checks spelling only, not handwriting or meaning.
- Focus games are short attention tasks for practice; a result never says anything about attention "problems".
- Estimates are Bayesian ranges; with few exercises they are rough. Difficulty is designed, not calibrated.
  Validation uses simulated users, not real populations.
- Speed-based scoring can disadvantage some users; calm mode removes the time pressure.
- The collaboration score is partly keyword-based (English only) and not validated.
- Projections are scenarios with uncertainty bands, never certainties.
""")
