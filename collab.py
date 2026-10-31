"""AI Collaboration Score (0-100).

Score = 0.20*Clarification + 0.25*Critical verification + 0.20*Iteration
        + 0.20*Autonomy + 0.15*Responsible use          (weights = design proposal, not validated)

Components (0-100):
- Clarification, Iteration: share of the user's messages with clarifying questions / refinement requests
  (keyword heuristics, English only).
- Critical verification: MEASURED IN SITUATION when >= 3 "spot-the-error" challenges were done
  (the coach states a claim about the user's own profile, half are deliberately wrong; score = how well the
  user verifies and decides). Otherwise falls back to a keyword heuristic.
- Autonomy: 100 * (1 - hint rate) on exercises.
- Responsible use: 100 - 40 per "give me the answer" request - 30 per personal contact detail shared.
"""
import re

WEIGHTS = dict(clarification=0.20, verification=0.25, iteration=0.20, autonomy=0.20, responsible=0.15)
MIN_PROBES = 3

PAT = dict(
    clarification=r"\b(what do you mean|clarify|could you explain|can you explain|specifically|for example|in other words|do you mean|what is the difference)\b",
    verification=r"\b(why|source|evidence|are you sure|double[- ]check|how do you know|justify|prove|is that correct|verify|reference)\b",
    iteration=r"\b(instead|rephrase|try again|another|more|shorter|simpler|harder|easier|update|refine|adjust|change)\b",
    cheating=r"\b(give me the answer|just tell me the answer|do it for me|solve it for me|answers? only)\b",
    sensitive=r"([\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d ()-]{7,}\d)",  # e-mail / phone number
)


def _hit(msg, key):
    return bool(re.search(PAT[key], msg, re.I))


def _frac(msgs, fn, target_share):
    n = len(msgs)
    if n == 0:
        return 0.0
    hits = sum(fn(m) for m in msgs)
    return min(1.0, hits / max(1.0, target_share * n)) * 100


def score(user_msgs, trials_df, probes_df=None):
    n = len(user_msgs)
    clar = _frac(user_msgs, lambda m: _hit(m, "clarification") or ("?" in m and len(m.split()) >= 8), 0.3)
    itr = _frac(user_msgs, lambda m: _hit(m, "iteration"), 0.3)

    n_probes = 0 if probes_df is None else len(probes_df)
    if n_probes >= MIN_PROBES:
        veri = float(probes_df["score"].mean()) * 100
        source = f"measured in {n_probes} spot-the-error challenges"
    else:
        veri = _frac(user_msgs, lambda m: _hit(m, "verification"), 0.3)
        source = f"keyword heuristic (do {MIN_PROBES}+ spot-the-error challenges for a stronger measure)"

    done = trials_df
    if trials_df is not None and len(trials_df) and "abandoned" in trials_df:
        done = trials_df[trials_df["abandoned"].fillna(0) == 0]
    aut = 50.0 if done is None or len(done) == 0 else 100 * (1 - float(done["hint"].mean()))

    cheat = sum(_hit(m, "cheating") for m in user_msgs)
    sens = sum(_hit(m, "sensitive") for m in user_msgs)
    resp = max(0.0, 100 - 40 * cheat - 30 * sens)

    comps = dict(clarification=clar, verification=veri, iteration=itr, autonomy=aut, responsible=resp)
    total = sum(WEIGHTS[k] * v for k, v in comps.items())
    low = n < 5 and n_probes < MIN_PROBES
    return dict(score=round(total, 1), components={k: round(v, 1) for k, v in comps.items()},
                n_msgs=n, n_probes=n_probes, verification_source=source,
                confidence="low (little data yet)" if low else "medium")
