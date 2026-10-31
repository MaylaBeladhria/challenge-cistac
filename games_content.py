"""v6 interactive games (original content, English), shared by several profiles.

| Game                  | Skills (practice only)                      | Profiles where it is offered          |
|-----------------------|---------------------------------------------|---------------------------------------|
| Robot rescue          | selective attention, following instructions | ADHD                                  |
| Detective             | visual search, details, reasoning           | ADHD                                  |
| Pack your school bag  | organisation, priorities, autonomy          | ADHD, autism (routines)               |
| Emotion detective     | recognising emotions, calming strategies    | autism, ADHD (frustration)            |
| Treasure map          | memory, sequencing, planning, left/right    | ADHD, dyslexia (directions)           |
| Copy the rhythm       | listening, remembering sound sequences      | ADHD, dyslexia (rhythm & sounds)      |
| Space pause station   | noticing how you feel, calming down         | every profile (see app.py)            |

Each generator follows practice.py: (level 1-3, rng, ctx) -> item, and a NEW question each time.
New optional item fields used here:
  multi + answers   several things to pick (the child ticks boxes)
  accept            other answers that are also right ("a feeling does not have only one explanation")
  praise            the positive message shown when the answer is right
  rhythm + listen_first   a sound sequence played by the browser; at level 3 the answers appear after listening
"""
from practice import gen_id, item

# ------------------------------------------------------------------ 1. Robot rescue mission
COLOR_SHAPES = {  # colour -> {shape: emoji}
    "red": {"circle": "🔴", "square": "🟥", "heart": "❤️"},
    "blue": {"circle": "🔵", "square": "🟦", "heart": "💙"},
    "green": {"circle": "🟢", "square": "🟩", "heart": "💚"},
    "yellow": {"circle": "🟡", "square": "🟨", "heart": "💛"},
    "purple": {"circle": "🟣", "square": "🟪", "heart": "💜"},
}
SHAPES = ["circle", "square", "heart"]


def _factory(cells, cols):
    rows = [" ".join(cells[i:i + cols]) for i in range(0, len(cells), cols)]
    return ("<div style='display:flex;align-items:center;gap:1rem;justify-content:center'>"
            "<div style='font-size:3.2rem'>🤖</div>"
            "<div style='font-size:2.2rem;line-height:1.6;letter-spacing:.35em;padding:.6rem 1rem;border-radius:12px;"
            "background:repeating-linear-gradient(45deg,rgba(120,120,120,.08) 0 12px,rgba(120,120,120,.14) 12px 24px)'>"
            + "<br>".join(rows) + "</div></div>")


def robot(level, rng, ctx):
    cat = "Robot rescue"
    colors = rng.sample(list(COLOR_SHAPES), 3 if level == 1 else 4)
    if level == 1:  # colour only, few objects
        col, total, cols = colors[0], rng.randint(6, 8), 4
        shape = rng.choice(SHAPES)
        n = rng.randint(2, 4)
        cells = [COLOR_SHAPES[col][shape]] * n + [COLOR_SHAPES[rng.choice(colors[1:])][shape] for _ in range(total - n)]
        rule = f"Collect all the **{col.upper()}** objects."
        target = COLOR_SHAPES[col][shape]
        old = ""
    else:  # colour AND shape; level 3: the rule changed since the last round
        col, shape = colors[0], rng.choice(SHAPES)
        target = COLOR_SHAPES[col][shape]
        total, cols = (12, 4) if level == 2 else (15, 5)
        n = rng.randint(2, 5)
        look = [COLOR_SHAPES[col][s] for s in SHAPES if s != shape] + \
               [COLOR_SHAPES[c][shape] for c in colors[1:]]  # same colour OR same shape: tricky
        old = ""
        if level == 3:
            ocol = rng.choice(colors[1:])
            oshape = rng.choice([s for s in SHAPES if s != shape])
            old_t = COLOR_SHAPES[ocol][oshape]
            look.append(old_t)
            old = f"~~Last round: collect the {ocol} {oshape}s {old_t}.~~  \n🔄 **New rule for this round!** "
        cells = [target] * n + [rng.choice(look) for _ in range(total - n)]
        avoid = rng.choice([c for c in colors[1:]])
        rule = (f"Collect the **{col.upper()} {shape.upper()}S** only. "
                f"Avoid the {avoid} ones and everything else.")
    rng.shuffle(cells)
    choices = sorted({n - 1, n, n + 1, n + 2})
    return item(gen_id("robot", level, rule, *cells), cat, level,
                old + rule + "  \nHow many objects will the robot collect?", choices, n,
                f"There are {n} {target} to collect.", html=_factory(cells, cols), keep_order=True,
                praise="Bravo! You looked carefully at the objects. 🤖",
                hint="Say the rule again in your head, then check the objects one row at a time.")


# ------------------------------------------------------------------ 2. Detective investigation (drawn keys)
KEY_COLORS = {"yellow": "#f9c900", "blue": "#1e88e5", "red": "#e53935", "green": "#43a047"}


def key_svg(color, small, teeth, label):
    s = 0.62 if small else 1.0
    w, h = 120, 64
    teeth_svg = "".join(f"<rect x='{86 - 12 * k}' y='34' width='7' height='{12 + 4 * (k % 2)}' rx='1' "
                        f"fill='{KEY_COLORS[color]}' stroke='#333' stroke-width='1.5'/>" for k in range(teeth))
    body = (f"<circle cx='22' cy='28' r='15' fill='{KEY_COLORS[color]}' stroke='#333' stroke-width='2'/>"
            f"<circle cx='22' cy='28' r='6' fill='white' stroke='#333' stroke-width='1.5'/>"
            f"<rect x='35' y='23' width='62' height='11' rx='3' fill='{KEY_COLORS[color]}' stroke='#333' "
            f"stroke-width='2'/>{teeth_svg}")
    return (f"<div style='display:inline-block;text-align:center;margin:.3rem .5rem;vertical-align:bottom'>"
            f"<svg width='{w * s * 1.5:.0f}' height='{h * s * 1.5:.0f}' viewBox='0 0 {w} {h}' role='img' "
            f"aria-label='{'small' if small else 'big'} {color} key with {teeth} teeth'>"
            f"<g>{body}</g></svg><div style='font-weight:700'>{label}</div></div>")


def detective(level, rng, ctx):
    cat = "Detective"
    feats = ["color", "size", "teeth"][: level]  # level 1: one feature, 2: two, 3: three (clues from scenes)
    target = dict(color=rng.choice(list(KEY_COLORS)), size=rng.choice(["small", "big"]), teeth=rng.randint(1, 3))
    n = {1: 4, 2: 6, 3: 7}[level]
    keys = [target]
    while len(keys) < n:
        k = dict(color=rng.choice(list(KEY_COLORS)), size=rng.choice(["small", "big"]), teeth=rng.randint(1, 3))
        if all(k[f] == target[f] for f in feats):  # must differ in at least one asked feature
            continue
        if level == 3 and sum(k[f] == target[f] for f in feats) < 2 and rng.random() < 0.7:
            continue  # level 3: most suspects share 2 of the 3 clues
        keys.append(k)
    rng.shuffle(keys)
    ans = f"Key {keys.index(target) + 1}"
    desc = {"color": f"{target['color']}", "size": target["size"],
            "teeth": f"with {target['teeth']} {'tooth' if target['teeth'] == 1 else 'teeth'}"}
    if level < 3:
        words = ([desc["size"]] if "size" in feats else []) + [desc["color"]]
        q = f"🔎 Find the **{' '.join(words)} key**."
        why = f"{ans} is the only {' '.join(words)} key."
    else:
        q = ("🔎 Read the clues from the three scenes, then find the key.  \n"
             f"🏡 *Scene 1 (garden):* drops of **{target['color']}** paint near the door.  \n"
             f"🧸 *Scene 2 (toy room):* the key fits in a **{'tiny' if target['size'] == 'small' else 'large'}** box, "
             f"so it is **{target['size']}**.  \n"
             f"🚪 *Scene 3 (cellar):* the lock has **{target['teeth']}** hole{'s' if target['teeth'] > 1 else ''}, "
             f"so the key has {target['teeth']} {'tooth' if target['teeth'] == 1 else 'teeth'}.")
        why = f"{ans} is {target['size']}, {target['color']} and {desc['teeth']}: it matches all three clues."
    html = "<div style='text-align:center'>" + "".join(
        key_svg(k["color"], k["size"] == "small", k["teeth"], f"Key {i + 1}") for i, k in enumerate(keys)) + "</div>"
    return item(gen_id("detective", level, *[f"{k['color']}{k['size']}{k['teeth']}" for k in keys]), cat, level,
                q, [f"Key {i + 1}" for i in range(n)], ans, why, html=html, keep_order=True,
                praise="Case solved! You checked the clues carefully. 🕵️",
                hint="Check one clue at a time and cross out (in your head) the keys that do not match.")


# ------------------------------------------------------------------ 3. Pack your school bag
SUBJECTS = {"Maths": ["📏 Ruler", "🧮 Calculator"], "English": ["📗 English book", "📒 Word notebook"],
            "Art": ["🖍️ Crayons", "🖌️ Paintbrush"], "Sport": ["👟 Trainers", "🩳 Sports shorts"],
            "Music": ["🪈 Recorder", "🎼 Music book"], "Science": ["🔬 Science notebook", "🥽 Safety glasses"]}
NOT_SCHOOL = ["🧸 Teddy bear", "🎮 Game console", "🛹 Skateboard", "📺 TV remote", "🪀 Yo-yo", "🛁 Bath duck"]


def school_bag(level, rng, ctx):
    cat = "Pack your school bag"
    praise = "Your school bag is ready. You thought of the important things! 🎒"
    if level == 1:
        subj = rng.choice(list(SUBJECTS))
        ans = rng.choice(SUBJECTS[subj])
        others = [x for s, xs in SUBJECTS.items() if s != subj for x in xs]
        dist = rng.sample(others, 2) + rng.sample(NOT_SCHOOL, 1)
        return item(gen_id("bag1", subj, ans, *sorted(dist)), cat, level,
                    f"Tomorrow you have **{subj}**. Which one do you need?", [ans] + dist, ans,
                    f"For {subj} you need {ans}.", praise=praise)
    subs = rng.sample(list(SUBJECTS), 3)
    if level == 2:  # three subjects: tick everything you need
        need = [rng.choice(SUBJECTS[s]) for s in subs]
        others = [x for s, xs in SUBJECTS.items() if s not in subs for x in xs]
        dist = rng.sample(others, 2) + rng.sample(NOT_SCHOOL, 2)
        return item(gen_id("bag2", *need, *sorted(dist)), cat, level,
                    f"Tomorrow you have **{', '.join(subs[:2])} and {subs[2]}**. "
                    "Tick everything you need (one thing for each subject).", need + dist, " + ".join(need),
                    "You need: " + ", ".join(f"{x} ({s})" for x, s in zip(need, subs)) + ".",
                    multi=True, answers=need, praise=praise,
                    hint="Take the subjects one by one: what do you use in that lesson?")
    # level 3: use the checklist and check the bag
    listed = [x for s in subs for x in SUBJECTS[s]]
    packed = rng.sample(listed, rng.randint(2, 4))
    missing = [x for x in listed if x not in packed]
    extra = rng.choice(NOT_SCHOOL)
    checklist = "  \n".join(f"☐ **{s}**: {', '.join(SUBJECTS[s])}" for s in subs)
    return item(gen_id("bag3", *sorted(packed), extra), cat, level,
                f"📝 Your checklist for tomorrow:  \n{checklist}  \n\n🎒 Already in your bag: "
                f"{', '.join(packed + [extra])}.  \n**Tick what is still missing.**",
                missing + packed[:2] + [extra], " + ".join(missing),
                "Still missing: " + ", ".join(missing) + f". ({extra} is not on the list: it can stay at home.)",
                multi=True, answers=missing, praise=praise,
                hint="Go down the checklist line by line and look for each thing in the bag.")


# ------------------------------------------------------------------ 4. Emotion detective
FACES = {"😀": "happy", "😢": "sad", "😠": "angry", "😨": "scared", "😮": "surprised", "😤": "frustrated"}
SITUATIONS = [  # (situation, possible feelings, feelings that do not fit)
    ("{A}'s tower of blocks falls down just before the end.", ["😤 Frustrated", "😢 Sad"], ["😀 Happy", "😴 Sleepy"]),
    ("{A} is going to a new school tomorrow.", ["😟 Worried", "🤩 Excited"], ["😴 Sleepy", "😠 Angry"]),
    ("{A}'s friend gives back a broken toy.", ["😠 Angry", "😢 Sad"], ["😀 Happy", "😴 Sleepy"]),
    ("The class is going on a trip to the zoo.", ["🤩 Excited", "😀 Happy"], ["😢 Sad", "😠 Angry"]),
    ("{A} loses a board game against {B}.", ["😞 Disappointed", "😤 Frustrated"], ["🤩 Excited", "😴 Sleepy"]),
    ("A big dog runs towards {A}, barking.", ["😨 Scared", "😮 Surprised"], ["😴 Sleepy", "😀 Happy"]),
    ("{A} gets a surprise visit from grandma.", ["😮 Surprised", "😀 Happy"], ["😠 Angry", "😢 Sad"]),
    ("{A} has to wait a long time at the doctor's.", ["🥱 Bored", "😤 Impatient"], ["🤩 Excited", "😨 Scared"]),
]
STRATEGIES = [  # (feeling, situation, good ideas, not-so-good ideas)
    ("frustrated", "{A}'s tower falls down just before the end.",
     ["Take 3 slow breaths, then try again", "Ask someone to help build it"],
     ["Kick the blocks across the room", "Shout at a friend"]),
    ("angry", "{B} takes {A}'s pencil without asking.",
     ["Stop, breathe, then say: 'Please give it back'", "Ask the teacher for help"],
     ["Grab it back and push {B}", "Break {B}'s pencil"]),
    ("worried", "{A} is worried about a test tomorrow.",
     ["Tell a grown-up about the worry", "Practise a little, then do something calm"],
     ["Keep the worry secret all night", "Stay awake all night thinking about it"]),
    ("sad", "{A}'s best friend is away on holiday.",
     ["Draw a picture to give the friend later", "Play with someone else for a while"],
     ["Stay alone all week", "Decide never to have friends again"]),
    ("disappointed", "It rains and the picnic is cancelled.",
     ["Say 'that's a pity' and have an indoor picnic", "Choose another fun plan"],
     ["Cry and refuse everything all day", "Blame the family"]),
]


def emotions(level, rng, ctx):
    cat = "Emotion detective"
    if level == 1:
        face = rng.choice(list(FACES))
        close = {"😠": "😤", "😤": "😠"}.get(face)  # angry and frustrated look alike: never together
        dist = rng.sample([f for f in FACES if f not in (face, close)], 2)
        return item(gen_id("emo1", face, *sorted(dist)), cat, level, "How does this face feel?",
                    [FACES[f] for f in [face] + dist], FACES[face],
                    f"Look at the eyes and the mouth: this face looks {FACES[face]}.",
                    html=f"<div style='font-size:5rem;text-align:center'>{face}</div>",
                    praise="Well spotted! You read the face carefully. 🕵️")
    if level == 2:
        k = rng.randrange(len(SITUATIONS))
        sit, good, bad = SITUATIONS[k]
        ans = rng.choice(good)
        return item(gen_id("emo2", k), cat, level, f"{sit} How might they feel?", good + bad, ans,
                    f"{good[0].split(' ', 1)[1]} or {good[1].split(' ', 1)[1].lower()} are both possible: "
                    "a feeling does not always have only one explanation.",
                    accept=good, praise="Yes, that feeling makes sense here!")
    k = rng.randrange(len(STRATEGIES))
    feel, sit, good, bad = STRATEGIES[k]
    ans = rng.choice(good)
    return item(gen_id("emo3", k), cat, level, f"{sit} {{A}} feels **{feel}**. What could {{A}} do?",
                good + bad, ans, "Good ideas: " + " / ".join(good) + ". Pausing, asking for help or trying again "
                "help big feelings get smaller.", accept=good,
                praise="Great idea! A short pause can help when you feel frustrated or upset.")


# ------------------------------------------------------------------ 5. Treasure map
DIRS = {"up": (-1, 0, "⬆️"), "down": (1, 0, "⬇️"), "left": (0, -1, "⬅️"), "right": (0, 1, "➡️")}
THINGS = ["🔑 key", "🍎 apple", "🌲 tree", "⭐ star", "🐚 shell", "🍄 mushroom", "🦜 parrot", "🪙 coin"]


def _grid_html(size, cells, start):
    rows = []
    for r in range(size):
        tds = []
        for c in range(size):
            v = "🧒" if (r, c) == start else cells.get((r, c), "")
            tds.append(f"<td style='width:3rem;height:3rem;text-align:center;font-size:1.8rem;"
                       f"border:1px solid rgba(120,100,60,.35)'>{v}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return ("<table style='margin:auto;border-collapse:collapse;background:rgba(240,210,140,.25);"
            "border-radius:10px'>" + "".join(rows) + "</table>")


def _say(steps):
    return ", then ".join(f"{n} step{'s' if n > 1 else ''} {DIRS[d][2]} {d}" for d, n in steps)


def _walk(start, steps, size, rocks=()):
    r, c = start
    for d, n in steps:
        for _ in range(n):
            r, c = r + DIRS[d][0], c + DIRS[d][1]
            if not (0 <= r < size and 0 <= c < size) or (r, c) in rocks:
                return None
    return (r, c)


def treasure(level, rng, ctx):
    cat = "Treasure map"
    size = 4 if level < 3 else 5
    start = (rng.randrange(size), rng.randrange(size))
    if level < 3:
        for _ in range(200):
            k = 1 if level == 1 else 3
            steps = []
            for _ in range(k):  # never the same direction twice in a row, never straight back
                prev = steps[-1][0] if steps else None
                bad = {prev, {"up": "down", "down": "up", "left": "right", "right": "left"}.get(prev)}
                steps.append((rng.choice([d for d in DIRS if d not in bad]), rng.randint(1, 2)))
            end = _walk(start, steps, size)
            if end and end != start:
                break
        free = [(r, c) for r in range(size) for c in range(size) if (r, c) not in (start, end)]
        things = rng.sample(THINGS, 4)
        cells = {end: things[0].split()[0]}
        for t, pos in zip(things[1:], rng.sample(free, 3)):
            cells[pos] = t.split()[0]
        ans = things[0]
        q = (f"Start at 🧒. Go **{_say(steps)}**. What do you find?" if level == 1
             else "You read the directions. Follow them on the map from 🧒: what do you find at the end?")
        extra = dict(memo=f"🗺️ Remember the directions: {_say(steps)}.", say=_say(steps)) if level == 2 else {}
        return item(gen_id("map", level, start, *steps, *sorted(cells.items())), cat, level, q, things, ans,
                    f"Following {_say(steps)} from 🧒 leads to the {ans}.", html=_grid_html(size, cells, start),
                    praise="You followed the directions and found it! 🗺️",
                    hint="Put your finger on 🧒 and move one square at a time, following the arrows ⬆️ ⬇️ ⬅️ ➡️.",
                    **extra)
    # level 3: plan a whole route around the rocks
    for _ in range(300):
        treasure_pos = (rng.randrange(size), rng.randrange(size))
        if abs(treasure_pos[0] - start[0]) + abs(treasure_pos[1] - start[1]) < 3:
            continue
        rocks = set(rng.sample([(r, c) for r in range(size) for c in range(size)
                                if (r, c) not in (start, treasure_pos)], 5))
        dr, dc = treasure_pos[0] - start[0], treasure_pos[1] - start[1]
        vert = ("down" if dr > 0 else "up", abs(dr))
        hor = ("right" if dc > 0 else "left", abs(dc))
        routes = [[s for s in r if s[1]] for r in ([vert, hor], [hor, vert])]
        good = [r for r in routes if _walk(start, r, size, rocks) == treasure_pos]
        bad = [r for r in routes if _walk(start, r, size, rocks) != treasure_pos]
        if len(good) == 1 and bad:
            flip = {"left": "right", "right": "left", "up": "down", "down": "up"}
            mirrored = [(flip[d] if d in ("left", "right") else d, n) for d, n in good[0]]
            wrongs = [bad[0]] + ([mirrored] if _walk(start, mirrored, size, rocks) != treasure_pos
                                 and mirrored != bad[0] else [])
            if len(wrongs) == 2:
                break
    else:
        return None  # no good map this time: the bank simply asks again
    cells = {p: "🪨" for p in rocks}
    cells[treasure_pos] = "💰"
    choices = [_say(good[0])] + [_say(w) for w in wrongs]
    return item(gen_id("map3", start, treasure_pos, *sorted(rocks)), cat, level,
                "Plan your route! Which directions take 🧒 to the treasure 💰 **without touching a rock 🪨**?",
                choices, choices[0], f"'{choices[0]}' goes around the rocks and reaches 💰.",
                html=_grid_html(size, cells, start), praise="You planned your route and found the treasure! 💰",
                hint="Try each route with your finger on the map. Stop if you touch a rock.")


# ------------------------------------------------------------------ 6. Copy the rhythm
SOUNDS = {"drum": "🥁", "bell": "🔔", "clap": "👏", "wood": "🪵"}


def _seq_text(seq):
    return " ".join(f"{SOUNDS[s]} {s}" for s in seq)


def rhythm(level, rng, ctx):
    cat = "Copy the rhythm"
    pool = ["drum", "bell", "clap"] if level == 1 else list(SOUNDS)
    n = {1: 2, 2: rng.choice([3, 4]), 3: rng.choice([5, 6])}[level]
    seq = [rng.choice(pool) for _ in range(n)]
    if len(set(seq)) == 1:
        seq[-1] = rng.choice([p for p in pool if p != seq[0]])
    wrong = set()
    for _ in range(60):
        w = seq[:]
        if rng.random() < 0.5 and n > 1:
            i = rng.randrange(n - 1)
            w[i], w[i + 1] = w[i + 1], w[i]
        else:
            i = rng.randrange(n)
            w[i] = rng.choice([p for p in pool if p != w[i]])
        if w != seq:
            wrong.add(tuple(w))
        if len(wrong) >= (2 if level == 1 else 3):
            break
    choices = [_seq_text(seq)] + [_seq_text(w) for w in sorted(wrong)]
    return item(gen_id("rhythm", *seq, *sorted(wrong)), cat, level,
                "🎧 Listen to the rhythm (press ▶ Play, as many times as you like). Which one is the same?",
                choices, choices[0], f"The rhythm was: {choices[0]}.", rhythm=seq, keep_order=False,
                listen_first=(level == 3), praise="You listened well and found the rhythm! 🥁",
                hint=f"The rhythm has {n} sounds. Tap them on the table while you listen.")


RHYTHM_JS = """
<div style="font-family:sans-serif;text-align:center">
<button id="p" style="font-size:1.2rem;padding:.5rem 1.4rem;border-radius:10px;border:1px solid #888;cursor:pointer">
▶ Play the rhythm</button><div id="s" style="font-size:2rem;height:2.6rem;margin-top:.4rem"></div></div>
<script>
const seq = __SEQ__; const icons = __ICONS__;
function play(){
  const ctx = new (window.AudioContext||window.webkitAudioContext)(); let t = ctx.currentTime + 0.15;
  const show = document.getElementById('s'); show.textContent='';
  seq.forEach((s,i)=>{
    const g = ctx.createGain(); g.connect(ctx.destination);
    if (s==='clap'){ const b = ctx.createBuffer(1, ctx.sampleRate*0.12, ctx.sampleRate); const d=b.getChannelData(0);
      for(let k=0;k<d.length;k++) d[k]=(Math.random()*2-1)*Math.pow(1-k/d.length,3);
      const src=ctx.createBufferSource(); src.buffer=b; src.connect(g); g.gain.value=0.8; src.start(t); }
    else { const o = ctx.createOscillator(); o.connect(g);
      const f = {drum:[90,'sine',0.35], bell:[880,'sine',0.9], wood:[700,'square',0.08]}[s];
      o.type=f[1]; o.frequency.setValueAtTime(f[0], t);
      if (s==='drum') o.frequency.exponentialRampToValueAtTime(45, t+0.3);
      g.gain.setValueAtTime(s==='wood'?0.25:0.9, t); g.gain.exponentialRampToValueAtTime(0.001, t+f[2]);
      o.start(t); o.stop(t+f[2]+0.05); }
    setTimeout(()=>{ show.textContent = '•'.repeat(i+1); }, (t-ctx.currentTime)*1000);
    t += 0.6; });
  setTimeout(()=>{ show.textContent='✔'; }, (t-ctx.currentTime)*1000);
}
document.getElementById('p').onclick = play;
</script>"""


def rhythm_player_html(seq):
    import json
    return RHYTHM_JS.replace("__SEQ__", json.dumps(seq)).replace("__ICONS__", json.dumps(SOUNDS))


# ------------------------------------------------------------------ 7. Space pause station
PAUSE_KINDS = {"star": "⭐ Breathe with the star", "planets": "🪐 Watch the planets float",
               "own": "🧑‍🚀 My own pause idea"}
OWN_IDEAS = ["💧 Drink some water", "🙆 Stretch up high, then relax", "🖐️ Squeeze your hands, then let go",
             "🎧 Sit somewhere quiet", "🌟 Think about something you love", "🚶 Walk slowly around the room"]


def pause_level(n_pauses):
    """Level 1: the breathing star only. Level 2: choose star or planets. Level 3: also your own pause idea."""
    return 1 if n_pauses < 1 else 2 if n_pauses < 3 else 3


def pause_html(kind, seconds, idea=""):
    if kind == "star":
        visual = ("<div id='v' style='font-size:5rem;animation:breathe 8s ease-in-out infinite'>⭐</div>"
                  "<div id='t' style='font-size:1.3rem;margin-top:.6rem'>Breathe in...</div>")
        js = ("let up=true; setInterval(()=>{up=!up; if(!stopped) document.getElementById('t').textContent="
              "up?'Breathe in...':'Breathe out...';},4000);")
    elif kind == "planets":
        visual = ("<div style='position:relative;height:9rem;overflow:hidden'>"
                  "<span style='position:absolute;font-size:3rem;left:10%;animation:float 9s ease-in-out infinite'>🪐</span>"
                  "<span style='position:absolute;font-size:2.4rem;left:45%;animation:float 12s ease-in-out infinite reverse'>🌍</span>"
                  "<span style='position:absolute;font-size:2rem;left:75%;animation:float 10s ease-in-out infinite'>🌙</span>"
                  "</div><div style='font-size:1.2rem'>Watch the planets float slowly. Breathe comfortably.</div>")
        js = ""
    else:
        visual = (f"<div style='font-size:2.6rem;margin:.8rem'>{idea.split(' ', 1)[0]}</div>"
                  f"<div style='font-size:1.4rem'>{idea.split(' ', 1)[-1]}</div>")
        js = ""
    return ("""<div style="font-family:sans-serif;text-align:center;padding:1rem;border-radius:16px;color:#fff;
background:radial-gradient(circle at 30% 20%,#2c3e7a,#0b1026)">
<style>@keyframes breathe{0%,100%{transform:scale(.6)}50%{transform:scale(1.25)}}
@keyframes float{0%,100%{top:1rem}50%{top:4.5rem}}</style>""" + visual + f"""
<div style="margin-top:.8rem;font-size:1.1rem">⏱ <span id="c">{seconds}</span> s</div>
<button id="b" style="margin-top:.6rem;font-size:1rem;padding:.35rem 1rem;border-radius:10px;border:0;cursor:pointer">
⏹ Stop when I want</button></div>
<script>let left={seconds}; let stopped=false;
const tick=setInterval(()=>{{ if(stopped) return; left-=1; document.getElementById('c').textContent=Math.max(left,0);
 if(left<=0){{ stopped=true; clearInterval(tick); document.getElementById('c').textContent='0 — well done!'; }} }},1000);
document.getElementById('b').onclick=()=>{{ stopped=true; clearInterval(tick);
 document.getElementById('c').textContent='stopped — well done!'; document.querySelectorAll('[style*=animation]')
 .forEach(e=>e.style.animationPlayState='paused'); }};
{js}</script>""")
