"""Explainable, non-clinical AI coach (3 modes: rule-based, free local LLM via Ollama, Anthropic API).

Architecture (justified): Brain Twin numbers + behaviour signals + self-reported mood -> structured context (JSON)
-> LLM that must cite the numbers behind each piece of advice -> output filter (clinical-term blocklist)
-> rule-based fallback. The fallback guarantees the coach works offline / without API key.
Mood is SELF-REPORTED by the user (no camera, no microphone) and only changes tone and session length.
"""
import json
import os
import re

CLINICAL = re.compile(
    r"\b(disorder|deficit|diagnos\w*|impair\w*|disease|pathology|syndrome|symptom\w*|patient|"
    r"clinical\w*|adhd|autis\w*|dyslex\w*|dementia|alzheimer\w*|illness|therapy|treatment|depress\w*|anxi\w*)\b", re.I)

SYSTEM = """You are a supportive cognitive-growth coach inside a learning app.
Rules:
- NON-CLINICAL: never diagnose, never use medical/clinical vocabulary, never compare to norms of illness.
  This is a learning tool, not a test. If asked about health concerns, say you cannot assess that
  and suggest talking to a qualified professional.
- EXPLAINABLE: for each piece of advice, state WHY using the numbers given (estimate, range, trials, behaviour).
- UNCERTAINTY: always mention the range; if trials < 5 say the estimate is still rough.
- Never present a future outcome as certain.
- Mood is self-reported by the user: never infer feelings yourself. If mood <= 2, suggest a lighter, shorter session.
- Write estimates as percentages (e.g. 39%). For an exercise suggestion about the focus dimension, use ITS OWN
  recommended_level and recommended_exercises from "question_focus", never the numbers of another dimension.
- Numbers in earlier messages may be outdated: use ONLY the numbers in USER DATA below.
- ANSWER THE QUESTION FIRST in 1-2 sentences, using the data of "question_focus" if present.
  Only afterwards mention the plan's top priority, and only if it is a different dimension. Never contradict yourself.
- If a range is wider than 40 points, say the estimate is still uncertain: do NOT call that area weak or strong.
- SUPPORT MODES (from "support_modes"): 'fun' = playful, short sentences; 'reading_support' = very short sentences,
  simple words; 'calm' = predictable, no time pressure, one idea at a time; 'focus' = very short, one quick goal,
  celebrate effort, suggest short rounds with a movement break. NEVER mention, guess or ask about any
  medical or developmental condition: the user only chose how they like to learn.
- "support_level" (mild / moderate / severe) was chosen by the parent: with 'severe', use very short sentences and
  propose a tiny, easy step. Never mention it or any condition.
- Be warm, concrete, short (max 120 words). Propose ONE next action.
- Encourage the user to verify your suggestions against their dashboard and to try before using hints."""

TIPS = dict(
    clarification="Try describing exactly what you want and giving an example.",
    verification="Check my claims against your dashboard, and ask me 'why?'.",
    iteration="Refine: ask me to make plans easier/harder or rephrase them.",
    autonomy="Try each exercise before opening a hint.",
    responsible="Avoid asking for answers directly and never share personal contact details.",
)


def _anthropic(system, messages):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    r = client.messages.create(model=os.getenv("COACH_MODEL", "claude-sonnet-5-5"),
                               max_tokens=500, system=system, messages=messages)
    return r.content[0].text


def _ollama(system, messages):
    """Free local LLM (https://ollama.com). No key, no internet needed, data never leaves the PC."""
    import urllib.request
    body = json.dumps({"model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"), "stream": False,
                       "messages": [{"role": "system", "content": system}] + messages,
                       "options": {"num_predict": 300}}).encode()
    req = urllib.request.Request(os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/chat",
                                 data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["message"]["content"]


def _llm(system, messages):
    """Provider order: COACH_PROVIDER=ollama (free, local) -> Anthropic API key -> None (rule-based coach)."""
    try:
        if os.getenv("COACH_PROVIDER", "").lower() == "ollama":
            return _ollama(system, messages)
        return _anthropic(system, messages)
    except Exception:
        return None


def _clean_history(history, user_msg):
    # Earlier coach answers contain OLD numbers: a small model copies them. Keep the turn, drop the content.
    outdated = "(earlier coach answer omitted: its numbers are outdated, use USER DATA only)"
    msgs = [{"role": m["role"], "content": outdated if m["role"] == "assistant" else m["text"]}
            for m in history[-8:]]
    if not msgs or msgs[-1]["content"] != user_msg:
        msgs.append({"role": "user", "content": user_msg})
    merged = []
    for m in msgs:  # API needs alternating roles starting with "user"
        if merged and merged[-1]["role"] == m["role"]:
            merged[-1]["content"] += "\n" + m["content"]
        else:
            merged.append(dict(m))
    while merged and merged[0]["role"] != "user":
        merged.pop(0)
    return merged


def _template(profile, plan, collab, behaviour, mood, support=None):
    best = max(profile, key=lambda d: profile[d]["mean"])
    top = plan[0]
    b, t = profile[best], profile[top["dim"]]
    weakest = min(collab["components"], key=collab["components"].get)
    txt = (f"Your strongest area so far is **{best}** (about {b['mean']:.0f}%, likely between "
           f"{b['lo']:.0f}% and {b['hi']:.0f}%).\n\n"
           f"Next focus: **{top['dim']}** (about {t['mean']:.0f}%, range {t['lo']:.0f}-{t['hi']:.0f}%, "
           f"{t['n']} exercises so far) because {top['reason']}. "
           f"Try {top['n_trials']} exercises at level {top['level']}/5.")
    if mood is not None and mood <= 2:
        txt += ("\n\nYou said your energy is low today, so a short, lighter session "
                "(3 exercises, one level easier) is a good choice.")
    if t["n"] < 5:
        txt += "\n\nThese estimates are still rough: a few more exercises will make them more reliable."
    if behaviour and behaviour.get("hint_rate") is not None and behaviour["hint_rate"] > 0.4:
        txt += (f"\n\nYou opened a hint in {behaviour['hint_rate'] * 100:.0f}% of exercises: "
                "try answering first, then check the hint.")
    if support and support.get("calm"):
        txt += "\n\nThere is no timer here: take your time, and stop whenever you like."
    if support and support.get("focus"):
        txt += "\n\nShort rounds work well: 5 questions, then a movement break, then come back for a new round."
    txt += f"\n\nCollaboration tip: {TIPS[weakest]}"
    return txt


def _focus(profile, user_msg):
    """Dimension the user asks about (matched on the full name or one of its words), else None."""
    if not user_msg:
        return None
    low = user_msg.lower()
    for d in profile:
        words = [w for w in d.lower().split() if len(w) > 4]
        if d.lower() in low or any(w in low for w in words):
            return d
    return None


def _facts(profile, plan, f):
    """Deterministic 'grounding footer': numbers computed by the code, never by the language model."""
    p = profile[f]
    fp = next(x for x in plan if x["dim"] == f)
    unc = " The estimate is still uncertain." if (p["hi"] - p["lo"]) > 40 or p["n"] < 5 else ""
    return (f"\n\n📊 Facts: {f} ≈ {p['mean']:.0f}% (95% range {p['lo']:.0f}-{p['hi']:.0f}%, "
            f"{p['n']} exercises).{unc} Suggested next step: {fp['n_trials']} exercises at level {fp['level']}/5.")


def reply(profile, plan, collab, history, user_msg=None, behaviour=None, mood=None, support=None, reading=None):
    f = _focus(profile, user_msg)
    fp = next((x for x in plan if f and x["dim"] == f), None)
    ctx = dict(question_focus=({"dimension": f, **{k: round(v, 1) for k, v in profile[f].items()},
                                "recommended_level": fp["level"], "recommended_exercises": fp["n_trials"],
                                "plan_top_priority": plan[0]["dim"]} if f else None),
               profile={d: {k: round(v, 1) for k, v in p.items()} for d, p in profile.items()},
               plan=plan[:3], collaboration=collab,
               behaviour={k: (round(v, 2) if isinstance(v, float) else v) for k, v in (behaviour or {}).items()},
               self_reported_mood_1_to_5=mood,
               support_modes=[name for name, key in (('fun', 'fun'), ('reading_support', 'reading'),
                                                     ('calm', 'calm'), ('focus', 'focus'))
                              if (support or {}).get(key)],
               age_band=(support or {}).get('age_band'), reading_practice=reading,
               support_level=(support or {}).get('severity') if (support or {}).get('profile') != 'typical' else None)
    system = SYSTEM + "\n\nUSER DATA (JSON):\n" + json.dumps(ctx, default=str)
    question = user_msg or "Give me a short summary of my progress and my next step."
    text = _llm(system, _clean_history(history, question))
    if text and not CLINICAL.search(text):
        return text + (_facts(profile, plan, f) if f else "")
    return _template(profile, plan, collab, behaviour, mood, support)
