"""Autism profile, final version: the 12 activities of "Activités interactives pour les enfants autistes".

Two kinds of activities (see the README table):
  QUESTION GAMES (added to the "Feelings & routines" bank, support_content.py, no timer, gentle feedback,
  several answers accepted when several are good):
    My day in cards · Change detective · Conversation bubbles · Clue puzzle · Solution box ·
    Mission: pack my bag · My interests world (quiz part)
  TOOLS WITHOUT RIGHT OR WRONG ANSWERS (tab "🧰 My tools", app.py):
    My day (planner) · Emotion radar (how do I feel?) · Talk board (pictograms, voice) · Choice shop ·
    My steps (one step at a time) · Sound studio (never automatic, always stoppable) · My interests world
Design rules taken from the document: speech is never required, "I don't know" and "none of these" are always
accepted, no time limit, no loud sound, no flashing, the child can stop at any time.
"""
from practice import gen_id, item

# ================================================================= 1. My day in cards
DAY = [("wake", "⏰", "Wake up"), ("dress", "👕", "Get dressed"), ("breakfast", "🥣", "Eat breakfast"),
       ("teeth", "🪥", "Brush teeth"), ("school", "🏫", "Go to school"), ("lunch", "🍽️", "Eat lunch"),
       ("play", "🧸", "Play"), ("homework", "📚", "Do homework"), ("dinner", "🍝", "Eat dinner"),
       ("bath", "🛁", "Take a bath"), ("story", "📖", "Story time"), ("sleep", "😴", "Go to sleep")]
EXTRA_CARDS = [("park", "🌳", "Go to the park"), ("shop", "🛒", "Go shopping"), ("swim", "🏊", "Swimming"),
               ("doctor", "🩺", "See the doctor"), ("grandma", "👵", "Visit grandma"), ("music", "🎵", "Music time"),
               ("snack", "🍎", "Snack"), ("draw", "🖍️", "Drawing"), ("tv", "📺", "TV time"), ("walk", "🐕", "Walk the dog")]
CARDS = {k: (e, t) for k, e, t in DAY + EXTRA_CARDS}


def card(k):
    e, t = CARDS[k]
    return f"{e} {t}"


def _cards_html(keys, hide=None, changed=None):
    out = []
    for k in keys:
        if k == hide:
            out.append("<div style='display:inline-block;width:6.2rem;margin:.2rem;padding:.4rem;border-radius:12px;"
                       "border:3px dashed #9e9e9e;text-align:center;font-size:2.4rem'>❓<div style='font-size:.85rem'>"
                       "What's next?</div></div>")
            continue
        e, t = CARDS[k]
        bd = "#ef6c00" if k == changed else "#90caf9"
        mark = "<div style='font-size:.75rem;color:#ef6c00;font-weight:700'>⚠️ changed today</div>" if k == changed else ""
        out.append(f"<div style='display:inline-block;width:6.2rem;margin:.2rem;padding:.4rem;border-radius:12px;"
                   f"border:3px solid {bd};text-align:center;vertical-align:top'><div style='font-size:2.4rem'>{e}</div>"
                   f"<div style='font-size:.85rem'>{t}</div>{mark}</div>")
    return "<div style='text-align:center'>" + " ➜ ".join(out) + "</div>"


def day_cards(level, rng, ctx):
    cat = "My day in cards"
    keys = [k for k, _, _ in DAY]
    if level == 1:  # what's next? two pictures, the other one is far away in the day
        i = rng.randrange(len(keys) - 1)
        far = rng.choice([k for j, k in enumerate(keys) if abs(j - (i + 1)) >= 4])
        plan = keys[max(0, i - 1): i + 1]
        return item(gen_id("day1", i, far), cat, level, f"What's next after **{card(keys[i])}**?",
                    [card(keys[i + 1]), card(far)], card(keys[i + 1]),
                    f"After {CARDS[keys[i]][1].lower()} usually comes {CARDS[keys[i + 1]][1].lower()}. "
                    "Every family's day can be a little different, and that is okay.",
                    html=_cards_html(plan + [keys[i + 1]], hide=keys[i + 1]), keep_order=True,
                    praise="Yes! You know what comes next. 📅")
    if level == 2:  # put 3-4 cards (far apart in the day) in order
        n = rng.choice([3, 4])
        parts = [[0, 1], [4, 5], [7, 8], [10, 11]]  # morning / midday / afternoon / night: the order is clear
        right = [keys[rng.choice(p)] for p in sorted(rng.sample(parts, n))]
        wrong = set()
        while len(wrong) < 2:
            w = right[:]
            rng.shuffle(w)
            if w != right:
                wrong.add(tuple(w))
        mixed = list(right)
        rng.shuffle(mixed)
        fmt = lambda ks: " ➜ ".join(CARDS[k][0] + " " + CARDS[k][1] for k in ks)  # noqa: E731
        return item(gen_id("day2", *right, *sorted(map(str, wrong))), cat, level,
                    "Put these cards in the order of the day. Which order is right?",
                    [fmt(right)] + [fmt(w) for w in wrong], fmt(right), "The day goes: " + fmt(right) + ".",
                    html=_cards_html(mixed), praise="Your day is in order! 📅")
    # level 3: the plan changed (announced in advance): what's next now?
    i = rng.randrange(2, len(keys) - 3)
    new = rng.choice(EXTRA_CARDS)[0]
    plan = keys[i - 1: i + 1] + [new] + keys[i + 2: i + 3]
    old = keys[i + 1]
    return item(gen_id("day3", i, new), cat, level,
                f"Today the plan changed: **{card(new)}** instead of **{card(old)}**. "
                f"You finished **{card(keys[i])}**. What's next now?",
                [card(new), card(old), card(keys[i + 2])], card(new),
                f"The new plan says {CARDS[new][1].lower()} comes next. {CARDS[old][1]} can come back another day.",
                html=_cards_html(plan, changed=new), praise="Well done! You followed the new plan. ⚠️➜✅")


# ================================================================= 5. Change detective
SCENES = [["🏠", "🌳", "🚗", "☀️", "🐕", "🚲"], ["🛏️", "🧸", "📚", "🪟", "💡", "🧦"], ["🍎", "🍌", "🥛", "🍞", "🧀", "🥕"],
          ["🏫", "🚌", "🎒", "✏️", "📏", "🕒"], ["🌊", "⛵", "🐚", "🦀", "☀️", "🏖️"]]
SWAPS = {"🚗": "🚌", "☀️": "🌧️", "🐕": "🐈", "🚲": "🛴", "🧸": "🤖", "📚": "📦", "💡": "🕯️", "🧦": "👟", "🍎": "🍐",
         "🍌": "🍇", "🥛": "🧃", "🍞": "🥐", "🧀": "🥚", "🥕": "🥦", "🚌": "🚕", "🎒": "👜", "✏️": "🖍️", "📏": "✂️",
         "🕒": "🕘", "⛵": "🚤", "🐚": "⭐", "🦀": "🐟", "🏖️": "⛱️", "🌳": "🌲", "🏠": "🏡", "🛏️": "🛋️", "🪟": "🚪",
         "🏫": "🏥", "🌊": "🏞️"}
CHANGE_STORIES = [
    ("The road to school is closed today 🚧.", ["Take another road with a grown-up", "Ask the grown-up which way to go"],
     ["Stay in the car and refuse to go", "Walk through the closed road"]),
    ("Your favourite cup is broken 💔☕.", ["Use another cup today", "Ask if you can choose a new cup"],
     ["Refuse to drink all day", "Throw the other cups"]),
    ("Your class moves to another room today 🏫➡️🚪.", ["Follow the teacher to the new room", "Ask where the new room is"],
     ["Stay alone in the old room", "Run out of school"]),
    ("Grandma comes to pick you up instead of mum 👵.", ["Say hello to grandma and go with her",
                                                         "Ask grandma why mum is not coming"],
     ["Hide and refuse to leave", "Go home alone"]),
    ("The swimming pool is closed, so the plan changes 🏊❌.", ["Choose another activity from the plan",
                                                               "Ask when swimming will happen again"],
     ["Be angry all day", "Go into the closed pool"]),
]


def change_detective(level, rng, ctx):
    cat = "Change detective"
    if level < 3:
        scene = rng.choice(SCENES)
        before = rng.sample(scene, 5 if level == 1 else 6)
        after = before[:]
        k = 1 if level == 1 else rng.choice([2, 3])
        pos = rng.sample(range(len(before)), k)
        for p in pos:
            after[p] = SWAPS.get(after[p], "❓")
        row = lambda xs: "<div style='font-size:2.4rem;letter-spacing:.35em'>" + " ".join(xs) + "</div>"  # noqa: E731
        html = ("<div style='text-align:center'><div style='font-weight:700'>Before</div>" + row(before)
                + "<div style='font-weight:700;margin-top:.4rem'>After</div>" + row(after) + "</div>")
        changed = [after[p] for p in sorted(pos)]
        same = [x for x in after if x not in changed]
        if level == 1:
            return item(gen_id("chg1", *before, *after), cat, level, "What is different? Look at the two pictures.",
                        changed + rng.sample(same, 2), changed[0],
                        f"{before[pos[0]]} became {changed[0]}.", html=html, praise="You spotted the change! 🔍")
        return item(gen_id("chg2", *before, *after), cat, level,
                    "Several things changed. **Tick everything that is new** in the 'After' picture.",
                    changed + rng.sample(same, 2), " + ".join(changed),
                    "The new things are: " + ", ".join(f"{before[p]} → {after[p]}" for p in sorted(pos)) + ".",
                    html=html, multi=True, answers=changed, praise="Great observing! You found the changes. 🔍")
    k = rng.randrange(len(CHANGE_STORIES))
    story, good, bad = CHANGE_STORIES[k]
    return item(gen_id("chg3", k), cat, level, f"{story} What could you do?", good + bad, good[0],
                "Both '" + good[0] + "' and '" + good[1] + "' are good ideas. Changes can feel hard: "
                "it is okay to take a little time.", accept=good,
                praise="Good idea! There is often another way when something changes. 🔄")


# ================================================================= 7. Conversation bubbles
def bubble(text, who="them"):
    side = "left" if who == "them" else "right"
    bg = "#e3f2fd" if who == "them" else "#e8f5e9"
    return (f"<div style='text-align:{side}'><span style='display:inline-block;max-width:80%;padding:.5rem .9rem;"
            f"margin:.2rem;border-radius:18px;background:{bg};font-size:1.15rem'>{text}</span></div>")


BUBBLES1 = [("{A} waves and says 'Hello!' 👋", "Hello!", ["Hello!", "Goodbye!"]),
            ("{A} gives you a pencil ✏️.", "Thank you!", ["Thank you!", "Hello!"]),
            ("It is the end of the day. {A} goes home 🏠.", "Goodbye!", ["Goodbye!", "Thank you!"]),
            ("You bump into {A} by mistake.", "Sorry!", ["Sorry!", "Goodbye!"]),
            ("You want the ball. You ask {A}:", "Please can I have the ball?", ["Please can I have the ball?",
                                                                                 "Goodbye!"])]
BUBBLES2 = [("{A}: 'Do you want to play with me?' 🧱", ["Yes, I want to play!", "I prefer to play alone, thank you."],
             ["Go away!", "(take {A}'s blocks)"]),
            ("{A}: 'Do you like my drawing?' 🖼️", ["Yes, I like the colours!", "It's nice. I like dogs better."],
             ["It's ugly!", "(tear the drawing)"]),
            ("{A}: 'What did you do at the weekend?'", ["I went to the park.", "I stayed home and played."],
             ["Why do you ask?!", "(shout)"]),
            ("{A}: 'Can I sit here?'", ["Yes, you can.", "Sorry, I need some space now."],
             ["(push {A})", "No! Never!"])]
DIALOGUES = [
    ["{A}: 'Hi! Can I play with you?'", ["Yes! We can build together.", "I prefer to play alone now."],
     "{A}: 'Okay! What are you building?'", ["A tower! 🏗️", "A train track 🚂", "I don't want to say."],
     ["(knock the tower down)"]],
    ["{A}: 'Hello! What's your name?'", ["My name is ...", "(show my name card)"],
     "{A}: 'Nice to meet you! Do you like football?'", ["Yes, I do! ⚽", "No, I like drawing. 🖍️", "I don't know."],
     ["(walk away without a word)"]],
]


def conversation(level, rng, ctx):
    cat = "Conversation bubbles"
    if level == 1:
        k = rng.randrange(len(BUBBLES1))
        sit, ans, ch = BUBBLES1[k]
        return item(gen_id("bub1", k), cat, level, f"{sit} What can you say?", ch, ans,
                    f"'{ans}' fits this situation. You can also wave or show a card instead of speaking.",
                    html=bubble(sit), say=ans, praise="That's a good thing to say! 💬")
    if level == 2:
        k = rng.randrange(len(BUBBLES2))
        q, good, bad = BUBBLES2[k]
        return item(gen_id("bub2", k), cat, level, "Which answer can you choose?", good + bad, good[0],
                    "Both kind answers are okay, even saying no politely. You choose what fits you.",
                    html=bubble(q), accept=good, praise="A kind answer! 💬")
    k = rng.randrange(len(DIALOGUES))
    first, r1, second, r2, bad = DIALOGUES[k]
    html = bubble(first) + bubble(rng.choice(r1), "me") + bubble(second)
    return item(gen_id("bub3", k), cat, level, "Continue the conversation: what can you answer?", r2 + bad, r2[0],
                "Any friendly answer works, even 'I don't want to say'. You never have to speak or look at "
                "people's eyes: a card or a gesture is fine too.", html=html, accept=r2,
                praise="Nice conversation! 💬")


# ================================================================= 9. Clue puzzle
ANIMALS = [("🐟", "fish", "🌊 the sea", "swims", "🫧 bubbles"), ("🐄", "cow", "🌾 the farm", "says moo", "🥛 milk"),
           ("🐒", "monkey", "🌴 the jungle", "climbs trees", "🍌 bananas"), ("🐧", "penguin", "🧊 the ice",
                                                                          "slides on ice", "🐟 fish"),
           ("🐝", "bee", "🌸 the flowers", "buzzes", "🍯 honey"), ("🐫", "camel", "🏜️ the desert", "walks on sand",
                                                                  "💧 little water"),
           ("🐿️", "squirrel", "🌳 the forest", "hides nuts", "🌰 nuts"), ("🐸", "frog", "🪷 the pond", "jumps",
                                                                         "🪰 flies")]


def clue_puzzle(level, rng, ctx):
    cat = "Clue puzzle"
    a = rng.choice(ANIMALS)
    others = rng.sample([x for x in ANIMALS if x != a], 2 if level == 1 else 3)
    if level == 1:  # associate two pictures that go together
        return item(gen_id("clue1", a[1], *[o[1] for o in others]), cat, level,
                    f"Which home goes with {a[0]} the **{a[1]}**?", [a[2]] + [o[2] for o in others], a[2],
                    f"The {a[1]} lives in {a[2].split(' ', 1)[1]}.", html=f"<div style='font-size:4rem;text-align:center'>"
                    f"{a[0]}</div>", praise="Yes! They go together. 🧩")
    clues = [f"🏠 It lives in {a[2]}.", f"🎬 It {a[3]}.", f"🍽️ It likes {a[4]}."]
    shown = clues[:2] if level == 2 else clues
    rng.shuffle(shown)
    return item(gen_id("clue", level, a[1], *[o[1] for o in others]), cat, level,
                "🔎 Look at the clues. Which animal is it?  \n" + "  \n".join(shown),
                [f"{a[0]} {a[1]}"] + [f"{o[0]} {o[1]}" for o in others], f"{a[0]} {a[1]}",
                "All the clues point to the " + a[1] + ". Every way of finding it is a good strategy.",
                praise="Puzzle solved! You used the clues. 🧩",
                hint="Read one clue, think of the animals that fit, then read the next clue.")


# ================================================================= 10. Solution box
PROBLEMS = [("You can't open a box 📦.", ["🙋 Ask for help", "🔄 Try another way", "☕ Take a break"],
             ["😡 Throw the box"]),
            ("Your shoelaces are untied 👟.", ["🙋 Ask a grown-up to help", "🪢 Try to tie them slowly",
                                               "🪑 Sit down to tie them"], ["🏃 Run and hope for the best"]),
            ("The room is too noisy 🔊.", ["🎧 Put on headphones", "🙋 Ask for a quiet place", "🚪 Go to the calm corner"],
             ["🗯️ Scream louder"]),
            ("You can't find your pencil ✏️.", ["🔎 Look in your pencil case again", "🙋 Ask to borrow one",
                                                "🧑‍🏫 Tell the teacher"], ["🙅 Stop working all day"]),
            ("Your tower keeps falling 🧱.", ["🔄 Build a bigger base", "☕ Take a short break", "🙋 Ask for help"],
             ["💥 Kick all the blocks"]),
            ("You don't understand the game rules 🎲.", ["🙋 Ask someone to explain", "👀 Watch one round first",
                                                         "📖 Look at the picture rules"], ["😶 Pretend and guess"]),
            ("Your jumper feels itchy 🧶.", ["🗣️ Tell a grown-up", "👕 Ask to change clothes",
                                             "🧥 Put a T-shirt underneath"], ["✂️ Cut it with scissors alone"])]


def solution_box(level, rng, ctx):
    cat = "Solution box"
    k = rng.randrange(len(PROBLEMS))
    prob, good, bad = PROBLEMS[k]
    g = rng.sample(good, 1 if level == 1 else len(good))
    choices = g + bad if level < 3 else good + bad + ["💭 Another idea of my own"]
    accept = [x for x in good + ["💭 Another idea of my own"] if x in choices]
    return item(gen_id("sol", level, k), cat, level, f"{prob} What could help?", choices, g[0],
                "Many solutions can help: asking for help, trying another way or taking a break are all good "
                "choices. You can also move away from something uncomfortable.", accept=accept,
                praise="That could help! There is more than one good solution. 🧰")


# ================================================================= 4. Mission: pack my bag
MISSIONS = {"school": ("🏫 school", ["📓 Notebook", "✏️ Pencil case", "💧 Water bottle", "🍎 Snack"]),
            "park": ("🌳 a trip to the park", ["🧢 Cap", "💧 Water bottle", "⚽ Ball", "🧴 Sun cream"]),
            "swimming": ("🏊 swimming", ["🩱 Swimsuit", "🏊 Towel", "🥽 Goggles", "🧴 Shampoo"]),
            "sport": ("⚽ sport", ["👟 Trainers", "🩳 Sports shorts", "💧 Water bottle", "🧦 Socks"]),
            "picnic": ("🧺 a picnic", ["🥪 Sandwich", "🍎 Fruit", "🧃 Juice", "🧻 Napkins"])}
NOT_NEEDED = ["🧹 Broom", "📺 TV remote", "🛁 Bath duck", "🪴 Plant pot", "🛏️ Pillow", "🍳 Frying pan"]
# (a comfort object like a teddy is never shown as "wrong": it can be a real need for the child)


def mission_bag(level, rng, ctx):
    cat = "Mission: pack my bag"
    m = rng.choice(list(MISSIONS))
    name, need = MISSIONS[m]
    praise = "Mission complete! Your bag is ready. 🎒"
    if level == 1:  # one needed thing between two pictures
        a = rng.choice(need)
        b = rng.choice(NOT_NEEDED)
        return item(gen_id("bag1", m, a, b), cat, level, f"Mission: pack your bag for **{name}**. What do you need?",
                    [a, b], a, f"For {name.split(' ', 1)[1]}, {a} is useful.", praise=praise)
    k = 3 if level == 2 else 4
    pick = rng.sample(need, k)
    dist = rng.sample(NOT_NEEDED, 2 if level == 2 else 3)
    return item(gen_id("bag", level, m, *sorted(pick), *sorted(dist)), cat, level,
                f"Mission: pack your bag for **{name}**. Tick what you need (take your time, no hurry).",
                pick + dist, " + ".join(pick), f"For {name.split(' ', 1)[1]}: " + ", ".join(pick) + ".",
                multi=True, answers=pick, praise=praise)


# ================================================================= 12. My interests world
THEMES = {
    "animals": ("🐾 Animals", [("🐬", "dolphin", "lives in the sea"), ("🦁", "lion", "lives in the savanna"),
                               ("🐘", "elephant", "has a long trunk"), ("🦉", "owl", "is awake at night"),
                               ("🐢", "turtle", "carries its shell"), ("🦒", "giraffe", "has a very long neck")]),
    "space": ("🚀 Space", [("🪐", "Saturn", "is the planet with big rings"), ("🔴", "Mars", "is the red planet"),
                          ("🌍", "Earth", "is the planet where we live"), ("🌙", "the Moon", "goes around the Earth"),
                          ("☀️", "the Sun", "is a star that gives us light"), ("🚀", "a rocket", "flies into space")]),
    "vehicles": ("🚂 Vehicles", [("🚂", "train", "runs on rails"), ("✈️", "plane", "flies in the sky"),
                                ("⛵", "sailing boat", "uses the wind on the water"), ("🚒", "fire engine",
                                                                                      "helps put out fires"),
                                ("🚜", "tractor", "works on the farm"), ("🚁", "helicopter", "can fly straight up")]),
    "dinosaurs": ("🦕 Dinosaurs", [("🦖", "T. rex", "had big teeth and ate meat"),
                                  ("🦕", "Brachiosaurus", "had a long neck and ate plants"),
                                  ("🌿", "Triceratops", "had three horns and ate plants"),
                                  ("🦴", "a fossil", "is a very old bone found in rocks"),
                                  ("🌋", "a volcano", "was there in the time of dinosaurs"),
                                  ("🥚", "a dinosaur egg", "is where baby dinosaurs came from")]),
}
TRAVEL = {"✈️ plane": "air", "🚁 helicopter": "air", "🎈 hot-air balloon": "air", "🚂 train": "land",
          "🚗 car": "land", "🚲 bike": "land", "🚜 tractor": "land", "⛵ sailing boat": "water", "🚢 ship": "water",
          "🛶 canoe": "water"}


def interests(level, rng, ctx):
    cat = "My interests world"
    theme = ctx.get("theme") if ctx.get("theme") in THEMES else rng.choice(list(THEMES))
    title, items = THEMES[theme]
    if level == 1:  # favourite between two: every answer is right
        a, b = rng.sample(items, 2)
        ch = [f"{a[0]} {a[1]}", f"{b[0]} {b[1]}"]
        return item(gen_id("int1", theme, a[1], b[1]), cat, level, f"{title}: which one do you like more?",
                    ch, ch[0], f"{a[1].capitalize()} {a[2]}, and {b[1]} {b[2]}. Both are great choices!",
                    accept=ch, praise="Good choice! This is your favourite. ⭐")
    if theme == "vehicles" and level == 2:
        v = rng.choice(list(TRAVEL))
        return item(gen_id("int2v", v), cat, level, f"Where does the **{v}** travel?",
                    ["🌍 on land", "☁️ in the air", "🌊 on water"],
                    {"land": "🌍 on land", "air": "☁️ in the air", "water": "🌊 on water"}[TRAVEL[v]],
                    f"The {v.split(' ', 1)[1]} travels " + {"land": "on land", "air": "in the air",
                                                             "water": "on water"}[TRAVEL[v]] + ".",
                    keep_order=True, praise="Yes! You know a lot about vehicles. 🚂")
    a = rng.choice(items)
    others = rng.sample([x for x in items if x != a], 2 if level == 2 else 3)
    return item(gen_id("int", level, theme, a[1]), cat, level, f"{title}: which one {a[2]}?",
                [f"{a[0]} {a[1]}"] + [f"{o[0]} {o[1]}" for o in others], f"{a[0]} {a[1]}",
                f"{a[1].capitalize()} {a[2]}.", praise="Yes! You are an expert. ⭐")


# ================================================================= TOOLS (no right or wrong answers)
FEELINGS = {"😀": "happy", "😢": "sad", "😠": "angry", "😨": "scared", "😌": "calm", "😴": "tired",
            "🤷": "I don't know"}
HELPERS = {"🗣️": "Talk to someone", "🙋": "Ask for help", "🎧": "Listen to a calm sound (Sound studio)",
           "☕": "Take a pause (Pause station)", "🧸": "Hold my teddy / a soft toy", "🏠": "Go to my quiet corner",
           "🤸": "Move my body a little", "🖍️": "Draw or do a calm activity"}
SUGGEST = {"happy": ["🗣️", "🖍️"], "sad": ["🗣️", "🧸", "🙋"], "angry": ["☕", "🤸", "🏠"], "scared": ["🙋", "🧸", "🗣️"],
           "calm": ["🖍️", "🎧"], "tired": ["☕", "🏠", "🎧"], "I don't know": ["☕", "🎧", "🗣️"]}

TALK_STARTERS = {"want": "🙋 I want", "dont": "🙅 I don't like", "help": "🆘 Help me", "more": "➕ More",
                 "stop": "✋ Stop", "pause": "☕ Pause"}
TALK_ITEMS = {"water": "💧 water", "food": "🍎 food", "toilet": "🚽 the toilet", "toy": "🧸 my toy", "hug": "🤗 a hug",
              "music": "🎵 music", "outside": "🌳 to go outside", "quiet": "🤫 quiet", "book": "📖 a book",
              "drawing": "🖍️ to draw", "sleep": "😴 to sleep", "noise": "🔊 this noise"}

SHOP = {"🍎 Food": ["🍎 Apple", "🍌 Banana", "🍕 Pizza", "🥕 Carrot", "🍪 Biscuit", "🧀 Cheese", "🍝 Pasta", "🥛 Milk"],
        "🧸 Toys": ["🧸 Teddy", "🧱 Blocks", "🚂 Train", "🧩 Puzzle", "🎨 Paints", "🪀 Yo-yo", "⚽ Ball", "🪁 Kite"],
        "👕 Clothes": ["👕 T-shirt", "👖 Trousers", "🧢 Cap", "🧦 Socks", "🧥 Coat", "👟 Trainers", "🧣 Scarf"],
        "🎲 Activities": ["🖍️ Drawing", "📖 Listen to a story", "🎵 Music", "🌳 Go outside", "🧩 Puzzle",
                         "🛝 Playground", "🍳 Cooking", "🧘 Quiet time"]}
SHOP_SITUATIONS = ["🧺 a picnic", "🌧️ a rainy afternoon", "🎂 a birthday party", "🚗 a long car trip",
                   "🏖️ a day at the beach"]

STEP_TASKS = {
    "shoes": ("👟 Put on my shoes", [("🪑", "Sit down"), ("👟", "Put my shoes on")]),
    "light": ("💡 Turn off the light", [("🚶", "Walk to the switch"), ("💡", "Press the switch")]),
    "water": ("🥤 Get a glass of water", [("🥤", "Get the cup"), ("🍶", "Take the bottle"), ("💧", "Pour the water"),
                                         ("↩️", "Put the bottle back")]),
    "hands": ("🧼 Wash my hands", [("🚰", "Wet my hands"), ("🧼", "Put on soap"), ("👐", "Rub my hands"),
                                  ("💦", "Rinse"), ("🧻", "Dry my hands")]),
    "teeth": ("🪥 Brush my teeth", [("🪥", "Put toothpaste on the brush"), ("😁", "Brush the top teeth"),
                                   ("😬", "Brush the bottom teeth"), ("🥛", "Rinse my mouth"), ("🧽", "Rinse the brush")]),
    "dress": ("👕 Get dressed", [("🩲", "Underwear"), ("👕", "T-shirt"), ("👖", "Trousers"), ("🧦", "Socks"),
                                ("👟", "Shoes")]),
    "bag": ("🎒 Pack my school bag", [("📅", "Look at tomorrow's plan"), ("📓", "Put in my notebooks"),
                                     ("✏️", "Put in my pencil case"), ("💧", "Add my water bottle"),
                                     ("🎒", "Close my bag"), ("🚪", "Put it by the door")]),
}
FLEXIBLE = {"dress": [1, 2]}  # level 3: the child may choose the order of these steps (T-shirt / trousers)


def steps_for_level(level):
    return [k for k, (_, st) in STEP_TASKS.items() if (len(st) == 2 if level == 1 else
                                                         3 <= len(st) <= 4 if level == 2 else len(st) >= 5)]


SOUNDS = {"rain": "🌧️ Rain", "waves": "🌊 Waves", "birds": "🐦 Birds", "wind": "🍃 Wind", "chimes": "🎐 Soft bells"}
VISUALS = {"colours": "🎨 Slow colours", "bubbles": "🫧 Floating bubbles", "stars": "✨ Quiet stars"}


def studio_html(kind, key):
    """Sound or visual explorer. Nothing starts automatically; low volume by default; stop at any time.
    Sounds are synthesised in the browser (Web Audio): no file, no download."""
    if kind == "sound":
        return """<div style="font-family:sans-serif;text-align:center;padding:.6rem;border-radius:14px;background:#eef6ff">
<button id="play" style="font-size:1.1rem;padding:.4rem 1rem;border-radius:10px;border:1px solid #888">▶ Play</button>
<button id="stop" style="font-size:1.1rem;padding:.4rem 1rem;border-radius:10px;border:1px solid #888">⏹ Stop</button>
<div style="margin-top:.5rem">🔉 Volume <input id="vol" type="range" min="0" max="0.6" step="0.02" value="0.15">
&nbsp; 🐢 Speed 🐇 <input id="spd" type="range" min="0.5" max="1.5" step="0.1" value="1"></div>
<div id="st" style="margin-top:.3rem;color:#555">Press Play when you want. You can stop at any time.</div></div>
<script>
const KIND = "__KEY__"; let ctx=null, master=null, nodes=[], timers=[];
function noise(){ const b=ctx.createBuffer(1, ctx.sampleRate*2, ctx.sampleRate), d=b.getChannelData(0); let last=0;
  for(let i=0;i<d.length;i++){ const w=Math.random()*2-1; last=(last+0.02*w)/1.02; d[i]= KIND==='waves'? last*3.5 : w; }
  const s=ctx.createBufferSource(); s.buffer=b; s.loop=true; return s; }
function lfo(target, f, depth, base){ const o=ctx.createOscillator(), g=ctx.createGain(); o.frequency.value=f;
  g.gain.value=depth; o.connect(g); g.connect(target); target.value=base; o.start(); nodes.push(o); return o; }
function start(){ stop(); ctx=new (window.AudioContext||window.webkitAudioContext)(); master=ctx.createGain();
  master.gain.value=+document.getElementById('vol').value; master.connect(ctx.destination);
  const spd=+document.getElementById('spd').value;
  if (KIND==='rain'||KIND==='wind'||KIND==='waves'){ const n=noise(), f=ctx.createBiquadFilter(), g=ctx.createGain();
    f.type = KIND==='wind' ? 'bandpass' : 'lowpass'; f.frequency.value = KIND==='rain'?1400:(KIND==='wind'?500:500);
    f.Q.value = KIND==='wind'?3:0.7; n.connect(f); f.connect(g); g.connect(master); n.start(); nodes.push(n);
    if (KIND==='wind') lfo(f.frequency, 0.12*spd, 250, 500);
    if (KIND==='waves') lfo(g.gain, 0.09*spd, 0.5, 0.55); }
  else { const tick=()=>{ if(!ctx) return; const t=ctx.currentTime, o=ctx.createOscillator(), g=ctx.createGain();
      o.connect(g); g.connect(master);
      if (KIND==='birds'){ o.frequency.setValueAtTime(2200+Math.random()*800,t); o.frequency.exponentialRampToValueAtTime(3600,t+0.09);
        g.gain.setValueAtTime(0.25,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.12); o.start(t); o.stop(t+0.15); }
      else { const notes=[523,587,659,784,880]; o.type='sine'; o.frequency.value=notes[Math.floor(Math.random()*5)];
        g.gain.setValueAtTime(0.3,t); g.gain.exponentialRampToValueAtTime(0.001,t+2.5); o.start(t); o.stop(t+2.6); }
      timers.push(setTimeout(tick, (KIND==='birds'? 400+Math.random()*1500 : 1200+Math.random()*1200)/spd)); };
    tick(); }
  document.getElementById('st').textContent='Playing softly... press Stop whenever you want.'; }
function stop(){ timers.forEach(clearTimeout); timers=[]; nodes.forEach(n=>{try{n.stop()}catch(e){}}); nodes=[];
  if(ctx){ctx.close(); ctx=null;} document.getElementById('st').textContent='Stopped.'; }
document.getElementById('play').onclick=start; document.getElementById('stop').onclick=stop;
document.getElementById('vol').oninput=e=>{ if(master) master.gain.value=+e.target.value; };
</script>""".replace("__KEY__", key)
    anim = {"colours": "<div id='v' style='height:150px;border-radius:14px;animation:col 24s linear infinite'></div>",
            "bubbles": "<div id='v' style='position:relative;height:150px;border-radius:14px;background:#e0f7fa;"
                       "overflow:hidden'>" + "".join(
                f"<span style='position:absolute;left:{x}%;bottom:-30px;font-size:{s}rem;animation:up {d}s linear "
                f"{dl}s infinite'>🫧</span>" for x, s, d, dl in ((10, 1.6, 14, 0), (30, 1.1, 18, 3), (55, 2, 16, 6),
                                                                 (75, 1.3, 20, 2), (88, 1.7, 15, 8))) + "</div>",
            "stars": "<div id='v' style='position:relative;height:150px;border-radius:14px;background:#141a3a;"
                     "overflow:hidden'>" + "".join(
                f"<span style='position:absolute;left:{x}%;top:{y}%;font-size:1.2rem;animation:tw {d}s ease-in-out "
                f"infinite'>✨</span>" for x, y, d in ((12, 20, 7), (35, 60, 9), (55, 25, 8), (72, 70, 10),
                                                         (85, 35, 7.5), (25, 80, 9.5))) + "</div>"}[key]
    return ("""<style>@keyframes col{0%{background:#cfe8ff}33%{background:#d9f7d9}66%{background:#fde9c8}
100%{background:#cfe8ff}}@keyframes up{from{transform:translateY(0)}to{transform:translateY(-220px)}}
@keyframes tw{0%,100%{opacity:.55}50%{opacity:1}}</style>
<div style="font-family:sans-serif;text-align:center">""" + anim + """
<button id="b" style="margin-top:.5rem;font-size:1rem;padding:.3rem 1rem;border-radius:10px;border:1px solid #888">
⏸ Pause / ▶ Play</button></div><script>let on=true;document.getElementById('b').onclick=()=>{on=!on;
document.querySelectorAll('#v, #v span').forEach(e=>e.style.animationPlayState=on?'running':'paused');};</script>""")
