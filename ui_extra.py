"""Interactive screens of the final version (called from app.py).

  tools_tab(C)  🧰 My tools (autism): My day · Emotion radar · Talk board · Choice shop · My steps ·
                Sound studio · My interests world      -> no right or wrong answers, speech never required
  build_tab(C)  🧱 Build & read (dyslexia): Build the word · Sentence puzzle · Magic echo · My story in pictures
  talk_quick(C) small talk board in the sidebar, available during every activity (autism / calm mode)

C is a small dict from app.py: user, S (settings), q_cap, speak (text-to-speech function), df_act, rules (degree).
"""
import random
import time

import streamlit as st
import streamlit.components.v1 as components

import autism_content as au
import dyslexia_content as dy
import engine
from practice import level_from_history

ss = st.session_state
LEVEL_NAMES = {1: "1 · Discovery", 2: "2 · Training", 3: "3 · Autonomy"}


def _tool_level(C, key):
    """Tools: the parent / child chooses the level; the default follows the degree chosen in the profile."""
    default = {"severe": 1, "moderate": 2}.get(C["S"].get("severity"), 2)
    default = min(default, C["q_cap"])
    return st.select_slider("Level", options=[1, 2, 3], value=default, format_func=LEVEL_NAMES.get,
                            key=f"{key}_lvl_{C['user']}")


def _log(C, cat, ok=True, level=1, domain="tools", item_id=0):
    engine.log_activity(C["user"], cat, item_id, level, ok, domain)


def _chip(text, bg="#e3f2fd", big=False):
    size = "1.5rem" if big else "1.15rem"
    return (f"<span style='display:inline-block;margin:.2rem;padding:.35rem .8rem;border-radius:12px;"
            f"background:{bg};font-size:{size}'>{text}</span>")


# ============================================================ sidebar quick talk board
QUICK = [("🙋", "Help me, please."), ("✋", "Stop, please."), ("☕", "I need a pause."), ("🚽", "I need the toilet."),
         ("💧", "I want water, please."), ("🤫", "I need quiet, please.")]


def talk_quick(C):
    with st.sidebar.expander("🗣️ Talk board (always here)", expanded=False):
        st.caption("Press a picture: the message is shown and said aloud. Speaking is never required.")
        cols = st.columns(3)
        for k, (e, txt) in enumerate(QUICK):
            if cols[k % 3].button(e, key=f"qt_{k}", help=txt):
                ss.talk_msg = txt
                C["speak"](txt, 0.9)


def talk_banner(C):
    if ss.get("talk_msg"):
        a, b = st.columns([5, 1])
        a.warning(f"🗣️ **{C['user']} says: {ss.talk_msg}**")
        if b.button("✔ OK", key="talk_ok"):
            ss.talk_msg = None
            st.rerun()


# ============================================================ 🧰 My tools (autism)
def tools_tab(C):
    st.subheader("🧰 My tools")
    st.caption("Plan my day, say how I feel, ask for things, choose, follow steps, explore sounds and my favourite "
               "things. **There are no right or wrong answers here**, speaking is never required, and you can stop "
               "at any time.")
    tools = {"📅 My day": my_day, "🎯 Emotion radar": emotion_radar, "🗣️ Talk board": talk_board,
             "🛒 Choice shop": choice_shop, "✅ My steps": my_steps, "🎧 Sound studio": sound_studio,
             "🌍 My interests": interests_world}
    t = st.radio("Choose a tool", list(tools), horizontal=True, key="tl_tool")
    tools[t](C)


# ---------------------------------------------------------- 📅 My day
DEFAULT_DAY = ["wake", "breakfast", "school", "play", "dinner", "sleep"]


def _plan(C):
    return engine.kv_get(C["user"], "day_plan", {"cards": DEFAULT_DAY, "done": [], "changed": None})


def _save_plan(C, p):
    engine.kv_set(C["user"], "day_plan", p)


def _plan_html(p):
    cells, now = [], None
    for i, k in enumerate(p["cards"]):
        e, t = au.CARDS[k]
        done = i in p["done"]
        if not done and now is None:
            now = i
        tag = "✅ Done" if done else ("▶ Now" if i == now else ("Next" if now is not None and i == now + 1 else ""))
        bd = "#2e7d32" if i == now else "#ef6c00" if p.get("changed") == i else "#90caf9"
        op = ".45" if done else "1"
        warn = "<div style='font-size:.72rem;color:#ef6c00;font-weight:700'>⚠️ changed today</div>" \
            if p.get("changed") == i else ""
        cells.append(f"<div style='display:inline-block;width:6.4rem;margin:.2rem;padding:.4rem;border-radius:12px;"
                     f"border:3px solid {bd};text-align:center;vertical-align:top;opacity:{op}'>"
                     f"<div style='font-size:2.3rem'>{e}</div><div style='font-size:.85rem'>{t}</div>"
                     f"<div style='font-size:.75rem;font-weight:700'>{tag}</div>{warn}</div>")
    return "<div>" + "".join(cells) + "</div>", now


def my_day(C):
    st.markdown("**📅 My day in cards** — *What's next?*")
    lvl = _tool_level(C, "day")
    p = _plan(C)
    html, now = _plan_html(p)
    st.markdown(html, unsafe_allow_html=True)
    if now is not None:
        a, b = st.columns(2)
        if a.button(f"✔ I finished: {au.card(p['cards'][now])}", key="day_done"):
            p["done"].append(now)
            _save_plan(C, p)
            nxt = now + 1
            ss.day_msg = (f"Well done! Next: {au.card(p['cards'][nxt])}." if nxt < len(p["cards"])
                          else "Your day plan is finished. 🌙")
            C["speak"](ss.day_msg, 0.9)
            st.rerun()
        if b.button("🔄 New day (uncheck all)", key="day_reset"):
            p["done"], p["changed"] = [], None
            _save_plan(C, p)
            st.rerun()
    else:
        st.success("Everything is done for today. 🌙")
        if st.button("🔄 New day", key="day_reset2"):
            p["done"], p["changed"] = [], None
            _save_plan(C, p)
            st.rerun()
    if ss.get("day_msg"):
        st.info(ss.day_msg)
    st.divider()
    if lvl == 1:  # what's next? two pictures
        if now is None or now + 1 >= len(p["cards"]):
            st.caption("Press 'New day' to play 'What's next?' again.")
            return
        st.markdown(f"**What's next after {au.card(p['cards'][now])}?**")
        nxt = p["cards"][now + 1]
        far = next(k for k in reversed(p["cards"]) if k not in (nxt, p["cards"][now])) \
            if len(p["cards"]) > 2 else "sleep"
        opts = sorted([nxt, far], key=lambda k: hash((k, ss.get("day_seed", 0))))
        cols = st.columns(2)
        for col, k in zip(cols, opts):
            if col.button(au.card(k), key=f"day_pick_{k}", use_container_width=True):
                ok = k == nxt
                ss.day_msg = (f"Yes! After {au.CARDS[p['cards'][now]][1].lower()} comes {au.CARDS[nxt][1].lower()}."
                              if ok else f"Look at the plan: next is {au.card(nxt)}.")
                _log(C, "My day", ok, 1)
                st.rerun()
    elif lvl == 2:  # put 3-4 cards in order
        st.markdown("**🧩 Put these cards in the order of my day** (press them one after the other).")
        if "day_game" not in ss or st.button("🔁 Other cards", key="day_new"):
            parts = [[0, 1], [4, 5], [7, 8], [10, 11]]
            keys = [k for k, _, _ in au.DAY]
            right = [keys[random.choice(x)] for x in sorted(random.sample(parts, random.choice([3, 4])))]
            mixed = right[:]
            while mixed == right:
                random.shuffle(mixed)
            ss.day_game = dict(right=right, mixed=mixed, built=[])
        g = ss.day_game
        st.markdown(" ➜ ".join(_chip(au.card(k), "#e8f5e9", True) for k in g["built"]) or "*(press the cards below)*",
                    unsafe_allow_html=True)
        cols = st.columns(len(g["mixed"]))
        for col, k in zip(cols, g["mixed"]):
            if k not in g["built"] and col.button(au.card(k), key=f"day_ord_{k}", use_container_width=True):
                g["built"].append(k)
                if len(g["built"]) == len(g["right"]):
                    ok = g["built"] == g["right"]
                    ss.day_msg = ("Your day is in order! 📅" if ok else
                                  "Almost! The day goes: " + " ➜ ".join(au.card(x) for x in g["right"]) + ".")
                    _log(C, "My day", ok, 2)
                    del ss["day_game"]
                st.rerun()
        if g["built"] and st.button("⌫ Undo", key="day_undo"):
            g["built"].pop()
            st.rerun()
    else:  # level 3: make my own plan, change it (changes announced in advance)
        st.markdown("**✏️ Make my own plan** (with help if needed). Changes can be shown in advance with ⚠️.")
        a, b = st.columns([3, 1])
        new = a.selectbox("Add a card", list(au.CARDS), format_func=au.card, key="day_add_sel")
        if b.button("➕ Add", key="day_add"):
            p["cards"].append(new)
            _save_plan(C, p)
            st.rerun()
        for i, k in enumerate(p["cards"]):
            c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 1, 2])
            c1.markdown(au.card(k) + (" ✅" if i in p["done"] else ""))
            if c2.button("⬆️", key=f"day_up_{i}", disabled=i == 0):
                p["cards"][i - 1], p["cards"][i] = p["cards"][i], p["cards"][i - 1]
                p["done"], p["changed"] = [], None
                _save_plan(C, p)
                st.rerun()
            if c3.button("⬇️", key=f"day_dn_{i}", disabled=i == len(p["cards"]) - 1):
                p["cards"][i + 1], p["cards"][i] = p["cards"][i], p["cards"][i + 1]
                p["done"], p["changed"] = [], None
                _save_plan(C, p)
                st.rerun()
            if c4.button("🗑", key=f"day_rm_{i}", disabled=len(p["cards"]) <= 2):
                p["cards"].pop(i)
                p["done"], p["changed"] = [], None
                _save_plan(C, p)
                st.rerun()
            if c5.button("⚠️ changed today", key=f"day_chg_{i}"):
                p["changed"] = None if p.get("changed") == i else i
                _save_plan(C, p)
                st.rerun()
        st.caption("The plan is a help, not a strict rule: it can change, and changes are shown in advance.")


# ---------------------------------------------------------- 🎯 Emotion radar
def emotion_radar(C):
    st.markdown("**🎯 How do you feel today?** You can choose a face, a colour, or 'I don't know'. "
                "You never have to explain.")
    lvl = _tool_level(C, "emo")
    faces = ["😀", "😢"] if lvl == 1 else list(au.FEELINGS)
    if lvl == 1 and "🤷" not in faces:
        faces.append("🤷")
    cols = st.columns(len(faces))
    for col, f in zip(cols, faces):
        if col.button(f"{f}\n{au.FEELINGS[f]}", key=f"emo_{f}", use_container_width=True):
            ss.emo_now = f
            ss.emo_help = None
            _log(C, au.FEELINGS[f], True, lvl, "checkin")
            st.rerun()
    colour = st.radio("My colour today (optional)", ["—", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬜"], horizontal=True,
                      key="emo_col")
    f = ss.get("emo_now")
    if not f:
        return
    feel = au.FEELINGS[f]
    st.success(f"You chose {f} **{feel}**" + (f" {colour}" if colour != "—" else "") + ". Thank you for telling me.")
    if lvl == 1:
        return
    st.markdown("**What could help?** (choose one, or none)")
    sugg = au.SUGGEST[feel]
    rest = [h for h in au.HELPERS if h not in sugg]
    opts = sugg + (rest if lvl == 3 else [])
    cols = st.columns(min(4, len(opts)))
    for k, h in enumerate(opts):
        if cols[k % len(cols)].button(f"{h} {au.HELPERS[h]}", key=f"emo_h_{h}", use_container_width=True):
            ss.emo_help = h
            st.rerun()
    if ss.get("emo_help"):
        h = ss.emo_help
        where = {"🎧": " Open the 🎧 Sound studio tool.", "☕": " Open the 🚀 Pause station tab."}.get(h, "")
        st.info(f"Good idea: {h} {au.HELPERS[h]}.{where}")


# ---------------------------------------------------------- 🗣️ Talk board
def talk_board(C):
    st.markdown("**🗣️ My talk board** — choose pictures to make a message. The message can be shown and said "
                "aloud. Speaking is never required.")
    lvl = _tool_level(C, "talk")
    msg = ss.setdefault("tb_msg", [])
    if lvl == 1:
        if "tb_pair" not in ss or st.button("🔁 Other pictures", key="tb_other"):
            ss.tb_pair = random.sample(list(au.TALK_ITEMS), 2)
        cols = st.columns(2)
        for col, k in zip(cols, ss.tb_pair):
            if col.button(f"🙋 I want {au.TALK_ITEMS[k]}", key=f"tb1_{k}", use_container_width=True):
                ss.tb_msg = ["want", k]
                C["speak"](_tb_text(ss.tb_msg), 0.9)
                st.rerun()
    else:
        st.markdown("**1. Start with:**")
        cols = st.columns(len(au.TALK_STARTERS))
        for col, (k, v) in zip(cols, au.TALK_STARTERS.items()):
            if col.button(v, key=f"tb_s_{k}", use_container_width=True):
                ss.tb_msg = [k]
                st.rerun()
        st.markdown("**2. Add a picture:**" + (" (you can add several)" if lvl == 3 else ""))
        items = list(au.TALK_ITEMS)
        for start in range(0, len(items), 6):
            cols = st.columns(6)
            for col, k in zip(cols, items[start:start + 6]):
                if col.button(au.TALK_ITEMS[k], key=f"tb_i_{k}", use_container_width=True):
                    if not msg:
                        msg.append("want")
                    if lvl == 2:
                        ss.tb_msg = msg[:1] + [k]
                    elif k not in msg:
                        msg.append(k)
                    st.rerun()
    if ss.get("tb_msg"):
        txt = _tb_text(ss.tb_msg)
        st.markdown(f"<div style='font-size:1.8rem;padding:.6rem 1rem;border-radius:14px;background:#fff3e0'>{txt}"
                    "</div>", unsafe_allow_html=True)
        a, b = st.columns(2)
        if a.button("🔊 Say it", key="tb_say"):
            C["speak"](txt, 0.9)
        if b.button("🧹 Clear", key="tb_clear"):
            ss.tb_msg = []
            st.rerun()


def _tb_text(msg):
    starter = au.TALK_STARTERS.get(msg[0], "🙋 I want") if msg and msg[0] in au.TALK_STARTERS else "🙋 I want"
    items = [au.TALK_ITEMS[k] for k in msg if k in au.TALK_ITEMS]
    if not items:
        return starter + "."
    joined = items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
    tail = ", please." if msg[0] in ("want", "help", "more") else "."
    return f"{starter} {joined}{tail}"


# ---------------------------------------------------------- 🛒 Choice shop
def choice_shop(C):
    st.markdown("**🛒 Choice shop** — choose what you like or need. *Every choice is okay, and 'none of these' too.*")
    lvl = _tool_level(C, "shop")
    cat = st.radio("Shelf", list(au.SHOP), horizontal=True, key="shop_cat")
    basket = engine.kv_get(C["user"], "basket", [])
    if lvl == 1:
        if ss.get("shop_pair_cat") != cat or st.button("🔁 Two other things", key="shop_other"):
            ss.shop_pair = random.sample(au.SHOP[cat], 2)
            ss.shop_pair_cat = cat
        cols = st.columns(3)
        for col, x in zip(cols, ss.shop_pair + ["🙅 None of these"]):
            if col.button(x, key=f"shop1_{x}", use_container_width=True):
                ss.shop_msg = "That's okay, none of these." if x.startswith("🙅") else f"I choose this one: {x}."
                C["speak"](ss.shop_msg, 0.9)
                _log(C, "Choice shop", True, 1)
                st.rerun()
        if ss.get("shop_msg"):
            st.success(ss.shop_msg)
        return
    situation = st.selectbox("For what?", ["Just for me"] + au.SHOP_SITUATIONS, key="shop_sit") if lvl == 3 else None
    picked = [x for x in au.SHOP[cat] if st.checkbox(x, value=x in basket, key=f"shop_cb_{cat}_{x}")]
    if st.button("🧺 Put in my basket", key="shop_put"):
        basket = [b for b in basket if b not in au.SHOP[cat]] + picked
        engine.kv_set(C["user"], "basket", basket)
        _log(C, "Choice shop", True, lvl)
        st.rerun()
    st.markdown("**🧺 My basket**" + (f" for {situation}" if situation and situation != "Just for me" else "") + ": "
                + (" ".join(_chip(b, "#fff3e0") for b in basket) if basket else "*empty*"), unsafe_allow_html=True)
    if basket and st.button("🔊 Say my choices", key="shop_say"):
        C["speak"]("I choose " + ", ".join(b.split(" ", 1)[1] for b in basket), 0.9)
    if basket and st.button("🧹 Empty my basket", key="shop_empty"):
        engine.kv_set(C["user"], "basket", [])
        st.rerun()


# ---------------------------------------------------------- ✅ My steps
def my_steps(C):
    st.markdown("**✅ My steps, at my own pace** — one step at a time. No time limit; you can pause, go back or "
                "start again.")
    lvl = _tool_level(C, "steps")
    tasks = au.steps_for_level(lvl)
    t = st.selectbox("Task", tasks, format_func=lambda k: au.STEP_TASKS[k][0], key=f"st_task_{lvl}")
    st_ = ss.get("steps")
    if not st_ or st_["task"] != t:
        st_ = ss.steps = dict(task=t, i=0, paused=False, order=list(range(len(au.STEP_TASKS[t][1]))), done=False)
    title, steps = au.STEP_TASKS[t]
    order = st_["order"]
    n = len(order)
    st.progress(st_["i"] / n, text=f"Step {min(st_['i'] + 1, n)} of {n}")
    st.markdown(" ".join(("✅" if j < st_["i"] else "👉" if j == st_["i"] else "⬜") + steps[order[j]][0]
                         for j in range(n)))
    if st_["done"]:
        st.success(f"Finished: {title}! 🌟 You did every step.")
        if st.button("🔁 Start again", key="st_again"):
            del ss["steps"]
            st.rerun()
        return
    if st_["paused"]:
        st.info("⏸ Paused. Take your time.")
        if st.button("▶ Resume", key="st_resume"):
            st_["paused"] = False
            st.rerun()
        return
    flex = au.FLEXIBLE.get(t, []) if lvl == 3 else []
    cur = order[st_["i"]]
    if cur in flex and not st_.get("chosen") and st_["i"] == min(order.index(x) for x in flex):
        st.markdown("**You can choose: which one first?**")
        cols = st.columns(len(flex))
        for col, j in zip(cols, flex):
            if col.button(f"{steps[j][0]} {steps[j][1]} first", key=f"st_flex_{j}"):
                rest = [x for x in flex if x != j]
                pos = st_["i"]
                st_["order"] = order[:pos] + [j] + rest + [x for x in order[pos:] if x not in flex]
                st_["chosen"] = True
                st.rerun()
    e, txt = steps[cur]
    st.markdown(f"<div style='text-align:center;padding:1rem;border-radius:16px;background:#e8f5e9'>"
                f"<div style='font-size:4.5rem'>{e}</div><div style='font-size:1.6rem'>{txt}</div></div>",
                unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    if a.button("✅ Done", key="st_ok", type="primary"):
        st_["i"] += 1
        if st_["i"] >= n:
            st_["done"] = True
            _log(C, "My steps", True, lvl)
        st.rerun()
    if b.button("⬅️ Back", key="st_back", disabled=st_["i"] == 0):
        st_["i"] -= 1
        st.rerun()
    if c.button("🔊 Listen", key="st_say"):
        C["speak"](txt, 0.85)
    if d.button("⏸ Pause", key="st_pause"):
        st_["paused"] = True
        st.rerun()


# ---------------------------------------------------------- 🎧 Sound studio
def sound_studio(C):
    st.markdown("**🎧 Sound & sensations studio** — nothing starts by itself, the volume starts low, and you can stop "
                "at any time. No flashing lights.")
    lvl = _tool_level(C, "studio")
    prefs = engine.kv_get(C["user"], "sensory_prefs", {})
    allx = {**{f"sound:{k}": v for k, v in au.SOUNDS.items()}, **{f"visual:{k}": v for k, v in au.VISUALS.items()}}
    pool = ["sound:rain", "visual:colours"] if lvl == 1 else list(allx)
    if lvl == 3:
        liked = [k for k in pool if prefs.get(k) == "like"]
        st.markdown("**🧰 My calm kit** (the things I like): "
                    + (", ".join(allx[k] for k in liked) if liked else "*empty: mark things with 👍 first*"))
        pool = liked or pool
    pick = st.radio("Explore", pool, format_func=lambda k: allx[k] + {"like": " 👍", "dislike": " 👎",
                                                                        "unsure": " 🤷"}.get(prefs.get(k), ""),
                    horizontal=True, key=f"studio_pick_{lvl}")
    kind, key = pick.split(":")
    components.html(au.studio_html(kind, key), height=150 if kind == "sound" else 230)
    if lvl >= 2:
        a, b, c = st.columns(3)
        for col, (val, lab) in zip((a, b, c), (("like", "👍 I like it"), ("dislike", "👎 I don't like it"),
                                               ("unsure", "🤷 I don't know"))):
            if col.button(lab, key=f"studio_{val}"):
                prefs[pick] = val
                engine.kv_set(C["user"], "sensory_prefs", prefs)
                st.rerun()


# ---------------------------------------------------------- 🌍 My interests world
def interests_world(C):
    themes = list(au.THEMES)
    saved = engine.kv_get(C["user"], "theme", themes[0])
    th = st.radio("My favourite world", themes, index=themes.index(saved) if saved in themes else 0,
                  format_func=lambda k: au.THEMES[k][0], horizontal=True, key="int_theme")
    if th != saved:
        engine.kv_set(C["user"], "theme", th)
    lvl = _tool_level(C, "int")
    title, items = au.THEMES[th]
    st.markdown(f"**{title}** — press 🔊 to hear about each one.")
    cols = st.columns(len(items))
    for col, (e, name, fact) in zip(cols, items):
        col.markdown(f"<div style='text-align:center;font-size:3rem'>{e}</div>"
                     f"<div style='text-align:center'>{name}</div>", unsafe_allow_html=True)
        if col.button("🔊", key=f"int_say_{name}", use_container_width=True):
            C["speak"](f"{name}. It {fact}." if not name.startswith(("the ", "a ")) else f"{name} {fact}.", 0.9)
    favs = engine.kv_get(C["user"], "favourites", {})
    if lvl == 1:
        if ss.get("int_pair_theme") != th or st.button("🔁 Two others", key="int_other"):
            ss.int_pair = random.sample(range(len(items)), 2)
            ss.int_pair_theme = th
        st.markdown("**Which one do you like more?**")
        cols = st.columns(2)
        for col, j in zip(cols, ss.int_pair):
            e, name, _ = items[j]
            if col.button(f"{e} {name}", key=f"int_fav_{j}", use_container_width=True):
                favs[th] = f"{e} {name}"
                engine.kv_set(C["user"], "favourites", favs)
                _log(C, "My interests", True, 1)
                st.rerun()
    elif lvl == 2:
        st.markdown("**🎮 A little game about my world**")
        if ss.get("int_q_theme") != th or "int_q" not in ss or st.button("▶ New question", key="int_newq"):
            ss.int_q = au.interests(2, random.Random(), {"theme": th})
            random.shuffle(ss.int_q["choices"])
            ss.int_q_theme = th
            ss.int_q_msg = None
        q = ss.int_q
        st.markdown(q["q"])
        ans = st.radio("Pick one", q["choices"], index=None, key=f"int_ans_{q['id']}")
        if st.button("Check", key="int_check") and ans:
            ok = ans == q["a"]
            ss.int_q_msg = (ok, (q["praise"] if ok else "Thanks for trying! ") + " " + q["why"])
            _log(C, "My interests", ok, 2)
        if ss.get("int_q_msg"):
            (st.success if ss.int_q_msg[0] else st.info)(ss.int_q_msg[1])
    else:
        st.markdown("**🎨 Create: my favourite sentence and my scene**")
        names = [f"{e} {n}" for e, n, _ in items]
        a, b = st.columns(2)
        fav = a.selectbox("This is my favourite...", names, key="int_s1")
        why = b.selectbox("because it is...", ["amazing", "big", "fast", "beautiful", "funny", "strong", "cute"],
                          key="int_s2")
        sentence = f"This is my favourite {fav.split(' ', 1)[1]} because it is {why}."
        st.markdown(f"<div style='font-size:1.5rem'>{fav.split(' ', 1)[0]} {sentence}</div>", unsafe_allow_html=True)
        scene = st.multiselect("Put things in my scene", names, default=names[:2], max_selections=5, key="int_scene")
        bg = {"animals": "#e8f5e9", "space": "#1a237e", "vehicles": "#e3f2fd", "dinosaurs": "#fff3e0"}[th]
        st.markdown(f"<div style='font-size:3rem;letter-spacing:.6em;text-align:center;padding:1rem;border-radius:16px;"
                    f"background:{bg}'>" + " ".join(s.split(" ", 1)[0] for s in scene) + "</div>",
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🔊 Read my sentence", key="int_read"):
            C["speak"](sentence, 0.9)
        if c2.button("💾 Save", key="int_save"):
            favs[th] = fav
            engine.kv_set(C["user"], "favourites", favs)
            engine.kv_set(C["user"], "my_scene", dict(theme=th, items=scene, sentence=sentence))
            _log(C, "My interests", True, 3)
            st.success("Saved! 🌟")
    if favs.get(th):
        st.caption(f"⭐ My favourite in this world: {favs[th]}")


# ============================================================ 🧱 Build & read (dyslexia)
def build_tab(C):
    st.subheader("🧱 Build & read")
    st.caption("Build words with letter tiles, put word cards in order, read along with the magic echo and create "
               "your own story. Listen as many times as you like: speed is never the goal.")
    acts = {"🔤 Build the word": build_word, "🧩 Sentence puzzle": sentence_puzzle, "🔊 Magic echo": magic_echo,
            "📖 My story in pictures": my_story}
    a = st.radio("Choose", list(acts), horizontal=True, key="br_act")
    acts[a](C)


def _lvl(C, cat):
    df = C["df_act"]
    h = df[(df.domain == "words") & (df.category == cat)] if len(df) else df
    return level_from_history(h, C["q_cap"])


def build_word(C):
    if st.button("▶ New word", key="bw_new") or "bw" not in ss:
        lvl = _lvl(C, "Build the word")
        used = ss.get("bw_used", [])
        pool = [w for w in dy.BUILD[lvl] if w[1] not in used] or dy.BUILD[lvl]
        emoji, word, parts = random.choice(pool)
        ss.bw_used = (used + [word])[-8:]
        extra = {1: 0, 2: 1, 3: 2}[lvl]
        dis = [dy.DISTRACT[p] for p in parts if p in dy.DISTRACT][:extra]
        tiles = parts + dis
        random.shuffle(tiles)
        ss.bw = dict(emoji=emoji, word=word, parts=parts, tiles=tiles, used=[], built=[], level=lvl, tries=0,
                     done=False, marks=None)
        if lvl == 1:  # level 1: the first tile is given (hints get fewer with the levels)
            k = tiles.index(parts[0])
            ss.bw["used"].append(k)
            ss.bw["built"].append(parts[0])
        C["speak"](word, 0.75)
    b = ss.bw
    lvl = b["level"]
    st.caption(f"Level {lvl} · " + {1: "picture + first letter given", 2: "picture only", 3: "listen only"}[lvl])
    top = st.columns([1, 3])
    if lvl < 3:
        top[0].markdown(f"<div style='font-size:4rem;text-align:center'>{b['emoji']}</div>", unsafe_allow_html=True)
    if top[1].button("🔊 Listen to the word", key="bw_listen"):
        C["speak"](b["word"], 0.7)
    boxes = []
    for i in range(len(b["parts"])):
        v = b["built"][i] if i < len(b["built"]) else "&nbsp;"
        col = "#fafafa"
        if b["marks"] is not None and i < len(b["marks"]):
            col = "#c8e6c9" if b["marks"][i] else "#ffcdd2"
        boxes.append(f"<span style='display:inline-block;min-width:3rem;margin:.15rem;padding:.4rem .5rem;"
                     f"border:2px solid #888;border-radius:10px;background:{col};font-size:2rem;text-align:center;"
                     f"font-family:Lexend,Verdana,sans-serif'>{v}</span>")
    st.markdown("<div style='text-align:center'>" + "".join(boxes) + "</div>", unsafe_allow_html=True)
    if b.get("msg") and not b["done"]:
        st.info(b["msg"])
    if b["done"]:
        st.success(f"'{b['word']}' — every letter helps to build the word. Well done! 🌟")
        return
    st.markdown("**Letter tiles** (press one: you hear its sound)")
    cols = st.columns(max(4, len(b["tiles"])))
    for k, t in enumerate(b["tiles"]):
        if k not in b["used"] and cols[k].button(t, key=f"bw_t_{k}", use_container_width=True):
            b["used"].append(k)
            b["built"].append(t)
            b["marks"] = None
            b["msg"] = None
            C["speak"](dy.SOUND_OF.get(t, t), 0.85)
            st.rerun()
    x, y, z = st.columns(3)
    if x.button("⌫ Undo", key="bw_undo", disabled=not b["built"]):
        b["built"].pop()
        b["used"].pop()
        b["marks"] = None
        st.rerun()
    if y.button("🧹 Clear", key="bw_clear"):
        b["built"], b["used"], b["marks"] = [], [], None
        st.rerun()
    if z.button("✔ Check", key="bw_check", type="primary"):
        ok = b["built"] == b["parts"]
        b["marks"] = [i < len(b["built"]) and b["built"][i] == p for i, p in enumerate(b["parts"])]
        if ok:
            b["done"] = True
            engine.log_activity(C["user"], "Build the word", 0, lvl, b["tries"] == 0, "words")
            C["speak"](f"{b['word']}. Well done!", 0.85)
        else:
            b["tries"] += 1
            b["msg"] = ("Every letter helps to build the word. Keep going! Listen again and fix the red boxes."
                        + (" 💡 The word starts with '" + b["parts"][0] + "'." if b["tries"] >= 2 else ""))
        st.rerun()


def sentence_puzzle(C):
    if st.button("▶ New sentence", key="sp_new") or "sp" not in ss:
        lvl = _lvl(C, "Sentence puzzle")
        cards = random.choice(dy.SENTENCE_CARDS[lvl])
        order = list(range(len(cards)))
        while order == sorted(order):
            random.shuffle(order)
        ss.sp = dict(cards=cards, order=order, built=[], level=lvl, tries=0, done=False, msg=None)
    s = ss.sp
    st.caption(f"Level {s['level']} · press the word cards in the right order (each card is read aloud)")
    pic = dy.SENTENCE_PICS.get(s["cards"][0], "")
    if pic and s["level"] == 1:
        st.markdown(f"<div style='font-size:3rem;text-align:center'>{pic}</div>", unsafe_allow_html=True)
    st.markdown("<div style='min-height:3rem'>" + " ".join(_chip(s["cards"][i], "#e8f5e9", True) for i in s["built"])
                + "</div>", unsafe_allow_html=True)
    if s["msg"]:
        (st.success if s["msg"][0] else st.info)(s["msg"][1])
    if s["done"]:
        return
    cols = st.columns(len(s["order"]))
    for col, i in zip(cols, s["order"]):
        if i not in s["built"] and col.button(s["cards"][i], key=f"sp_c_{i}", use_container_width=True):
            s["built"].append(i)
            s["msg"] = None
            C["speak"](s["cards"][i], 0.85)
            st.rerun()
    a, b, c = st.columns(3)
    if a.button("⌫ Undo", key="sp_undo", disabled=not s["built"]):
        s["built"].pop()
        st.rerun()
    if b.button("🔊 Read my sentence", key="sp_read", disabled=not s["built"]):
        C["speak"](" ".join(s["cards"][i] for i in s["built"]), 0.85)
    if c.button("✔ Check", key="sp_check", type="primary", disabled=len(s["built"]) < len(s["cards"])):
        if s["built"] == sorted(s["built"]):
            s["done"] = True
            s["msg"] = (True, "Your words are in the right order: the sentence makes sense! 🧩")
            engine.log_activity(C["user"], "Sentence puzzle", 0, s["level"], s["tries"] == 0, "words")
        else:
            s["tries"] += 1
            k = next(j for j, i in enumerate(s["built"]) if i != j)
            s["msg"] = (False, f"Card {k + 1} is not in the right place yet. Who or what is the sentence about? "
                               "Start with that card.")
            s["built"] = s["built"][:k]
        st.rerun()


def magic_echo(C):
    if st.button("▶ New text", key="me_new") or "me" not in ss:
        lvl = _lvl(C, "Magic echo")
        used = ss.get("me_used", [])
        pool = [t for t in dy.ECHO[lvl] if t not in used] or dy.ECHO[lvl]
        t = random.choice(pool)
        ss.me_used = (used + [t])[-6:]
        ss.me = dict(text=t, level=lvl, read=False)
    m = ss.me
    st.caption(f"Level {m['level']} · 1. Press 🔊 Listen and follow the words that light up (slow it down with 🐢). "
               "2. Then read it yourself, alone or with a grown-up.")
    components.html(dy.echo_html(m["text"]), height=150 + 40 * (m["level"] - 1))
    if not m["read"]:
        if st.button("✅ I read it myself", key="me_read", type="primary"):
            m["read"] = True
            engine.log_activity(C["user"], "Magic echo", 0, m["level"], True, "words")
            st.rerun()
    else:
        st.success("You can listen again and try again. Every reading is practice. 🌟")
    st.caption("Want the agent to check your reading word by word? Use the 📖 Reading practice tab.")


def my_story(C):
    lvl = _lvl(C, "My story")
    if st.button("▶ New story", key="ms_new") or "ms" not in ss or ss.ms.get("level") != lvl:
        k = random.randrange(len(dy.STORIES))
        order = [0, 1, 2]
        while order == [0, 1, 2]:
            random.shuffle(order)
        ss.ms = dict(k=k, level=lvl, order=order, built=[], done=False, msg=None)
    s = ss.ms
    pics, words, sents = dy.STORIES[s["k"]]
    st.caption(f"Level {lvl} · " + {1: "put the 3 pictures in order", 2: "complete the sentences with the word bank",
                                    3: "write your own story (helps are optional)"}[lvl])
    if s["msg"]:
        (st.success if s["msg"][0] else st.info)(s["msg"][1])
    if lvl == 1:
        st.markdown("<div style='font-size:3rem;text-align:center'>" + " ➜ ".join(pics[i] for i in s["built"])
                    + "</div>", unsafe_allow_html=True)
        if not s["done"]:
            cols = st.columns(3)
            for col, i in zip(cols, s["order"]):
                if i not in s["built"] and col.button(pics[i], key=f"ms_p_{i}", use_container_width=True):
                    s["built"].append(i)
                    if len(s["built"]) == 3:
                        ok = s["built"] == [0, 1, 2]
                        s["done"] = ok
                        s["msg"] = ((True, "You created a story! " + " ".join(sents)) if ok else
                                    (False, "Hmm, what happens first? Try again."))
                        if ok:
                            C["speak"](" ".join(sents), 0.85)
                        engine.log_activity(C["user"], "My story", 0, 1, ok, "words")
                        if not ok:
                            s["built"] = []
                    st.rerun()
        return
    if lvl == 2:
        st.markdown("<div style='font-size:2.6rem;text-align:center'>" + " ➜ ".join(pics) + "</div>",
                    unsafe_allow_html=True)
        answers = []
        for j, sent in enumerate(sents):
            w = words[j] if words[j] in sent else next((x for x in words if x in sent), None)
            if not w:
                st.markdown(f"{j + 1}. {sent}")
                continue
            left, right = sent.split(w, 1)
            a, b, c = st.columns([3, 2, 3])
            a.markdown(f"{j + 1}. {left}")
            pick = b.selectbox(" ", ["…"] + sorted(words), key=f"ms_sel_{s['k']}_{j}", label_visibility="collapsed")
            c.markdown(right)
            answers.append(pick == w)
        if st.button("✔ Check my story", key="ms_check"):
            ok = all(answers)
            s["msg"] = ((True, "You created a story. You can improve it step by step! 📖") if ok else
                        (False, f"{sum(answers)} of {len(answers)} words fit. Look at the pictures and try again."))
            engine.log_activity(C["user"], "My story", 0, 2, ok, "words")
            st.rerun()
        return
    st.markdown("<div style='font-size:2.6rem;text-align:center'>" + " ➜ ".join(pics) + "</div>",
                unsafe_allow_html=True)
    with st.expander("💡 Helps (optional): word bank and first words"):
        st.markdown("Word bank: " + " · ".join(f"**{w}**" for w in words + ["then", "and", "finally", "because"]))
        st.markdown("Start like this: *" + sents[0].split(" ")[0] + " ...*")
    text = st.text_area("Write 2 or 3 sentences about the pictures", key=f"ms_text_{s['k']}", height=110)
    a, b = st.columns(2)
    if a.button("🔊 Read my story", key="ms_say", disabled=not text.strip()):
        C["speak"](text, 0.85)
    if b.button("💾 Save my story", key="ms_save", disabled=not text.strip()):
        n = sum(text.count(x) for x in ".!?") or 1
        stories = engine.kv_get(C["user"], "stories", [])
        stories.append(dict(ts=time.strftime("%Y-%m-%d"), pics=pics, text=text.strip()))
        engine.kv_set(C["user"], "stories", stories[-20:])
        engine.log_activity(C["user"], "My story", 0, 3, n >= 2, "words")
        s["msg"] = (True, "You created a story. You can improve it step by step! 📖")
        st.rerun()
    saved = engine.kv_get(C["user"], "stories", [])
    if saved:
        with st.expander(f"📚 My saved stories ({len(saved)})"):
            for x in reversed(saved[-5:]):
                st.markdown(f"{' '.join(x['pics'])} — {x['text']}  \n*{x['ts']}*")
