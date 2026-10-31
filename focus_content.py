"""Focus & self-control practice (ADHD profile, original content, English).

Design choices for children who need help with focus, waiting and organising:
  - very short questions, one thing at a time, big visuals, immediate positive feedback and stars;
  - short rounds of 5 questions, then a MOVEMENT BREAK (moving is a good thing, not a punishment);
  - 4 of the 5 topics are generated, so the questions keep changing (see practice.py for the no-repeat rule).
Practice only: no screening, no score is ever interpreted as a sign of any condition.

Topics
  Spot the target       selective attention: count one picture among look-alikes
  Same or different?    attention to detail: compare two rows
  Stop & go             waiting / stopping: follow a GO / STOP rule (the rule flips at level 3)
  Follow the steps      keep instructions in mind: read the steps, hide them, answer
  Plan & self-control   everyday situations: waiting, asking, planning, calming down
  + v6 games (games_content.py): Robot rescue, Detective, Pack your school bag, Emotion detective,
    Treasure map, Copy the rhythm
"""
import random

import games_content as g
from practice import Bank, gen_id, item

CATEGORIES = ["Spot the target", "Same or different?", "Stop & go", "Follow the steps", "Plan & self-control",
              # v6 games
              "Robot rescue", "Detective", "Pack your school bag", "Emotion detective", "Treasure map",
              "Copy the rhythm"]

MOVES = ["Do 5 jumping jacks 🤸", "Stretch up high and count to 5 🙆", "Shake your hands like a wet dog 🐕",
         "March on the spot 10 times 🚶", "Take 3 slow 'balloon' breaths 🎈", "Touch your toes, then reach for the sky 🌤️",
         "Squeeze your fists tight, then let go ✊🖐️", "Do 5 frog jumps 🐸", "Roll your shoulders 5 times 🔄",
         "Stand on one foot and count to 5 🦩"]

LOOKALIKE = [["🐟", "🐠", "🐡"], ["🍏", "🍎", "🍐"], ["⭐", "🌟", "✨"], ["🚗", "🚕", "🚙"], ["🐶", "🐕", "🐩"],
             ["😀", "😃", "😄"], ["🌸", "🌺", "🌼"], ["🔵", "🟣", "🔷"]]
DIFFERENT = ["🍎", "🚗", "⭐", "🐶", "🎈", "🌸", "⚽", "🐸", "🍕", "🚀", "🧸", "🦋"]


def _grid_html(cells, cols):
    rows = [" ".join(cells[i:i + cols]) for i in range(0, len(cells), cols)]
    return ("<div style='font-size:2.4rem;line-height:1.6;letter-spacing:.35em;text-align:center;"
            "padding:.6rem;border-radius:12px;background:rgba(0,0,0,.04)'>" + "<br>".join(rows) + "</div>")


def _spot(level, rng, ctx):
    cols, rows = {1: (4, 3), 2: (5, 4), 3: (6, 5)}[level]
    if level == 1:
        target, *others = rng.sample(DIFFERENT, 3)
    elif level == 2:
        grp = rng.choice(LOOKALIKE)
        target = grp[0]
        others = [grp[1]] + rng.sample([d for d in DIFFERENT if d not in grp], 2)
    else:
        grp = rng.choice(LOOKALIKE)
        target, others = grp[0], grp[1:]
    n = rng.randint(2, {1: 5, 2: 7, 3: 9}[level])
    cells = [target] * n + [rng.choice(others) for _ in range(cols * rows - n)]
    rng.shuffle(cells)
    choices = sorted({n - 1, n, n + 1, n + 2})  # n >= 2, so 4 different positive numbers
    return item(gen_id("spot", *cells), "Spot the target", level, f"How many {target} can you find?",
                choices, n, f"There are {n} {target}. Going row by row helps you not miss any.",
                html=_grid_html(cells, cols), keep_order=True, hint="Go row by row and point with your finger.")


def _same(level, rng, ctx):
    k = {1: 3, 2: 5, 3: 7}[level]
    grp = rng.choice(LOOKALIKE) if level == 3 else None
    pool = DIFFERENT if level < 3 else DIFFERENT + grp
    row1 = [rng.choice(pool) for _ in range(k)]
    row2 = row1[:]
    same = rng.random() < 0.5
    where = ""
    if not same:
        i = rng.randrange(k)
        if level == 3 and rng.random() < 0.5 and k > 1:  # two neighbours swapped
            j = i + 1 if i < k - 1 else i - 1
            if row2[i] == row2[j]:
                row2[i] = rng.choice([p for p in pool if p != row2[i]])
            else:
                row2[i], row2[j] = row2[j], row2[i]
        else:
            alts = [g for g in (grp or []) if g != row2[i]] or [p for p in pool if p != row2[i]]
            row2[i] = rng.choice(alts)
        where = f" Look at place number {i + 1}."
    html = ("<div style='font-size:2.4rem;letter-spacing:.35em;text-align:center;line-height:1.7'>"
            + " ".join(row1) + "<br>" + " ".join(row2) + "</div>")
    ans = "✅ Same" if same else "❌ Different"
    return item(gen_id("same", *row1, "|", *row2), "Same or different?", level,
                "Are these two rows **exactly** the same?", ["✅ Same", "❌ Different"], ans,
                ("Yes, every picture matches." if same else "They are different." + where),
                html=html, keep_order=True, hint="Compare one picture at a time, from left to right.")


ANIMALS = ["🐶", "🐱", "🐰", "🐻", "🐸", "🐵", "🐷", "🐮", "🦊", "🐼"]


def _stopgo(level, rng, ctx):
    go_a, stop_a = rng.sample(ANIMALS, 2)
    if level == 1:
        rule = f"**GO** when you see {go_a}. **STOP** when you see {stop_a}."
        show = rng.choice([go_a, stop_a])
        ans = "👉 GO" if show == go_a else "✋ STOP"
        why = f"The rule says GO for {go_a} and STOP for {stop_a}."
        key = (go_a, stop_a, show)
    elif level == 2:
        rule = f"**GO** for every animal, **except** {stop_a}: then **STOP**!"
        show = stop_a if rng.random() < 0.4 else rng.choice([a for a in ANIMALS if a != stop_a])
        ans = "✋ STOP" if show == stop_a else "👉 GO"
        why = f"Every animal means GO, only {stop_a} means STOP."
        key = (stop_a, show)
    else:
        rule = (f"Green box 🟩: **GO** for {go_a}, **STOP** for the others.  \n"
                f"Red box 🟥: the rule **flips**: **STOP** for {go_a}, **GO** for the others.")
        box = rng.choice(["🟩", "🟥"])
        show = go_a if rng.random() < 0.5 else rng.choice([a for a in ANIMALS if a != go_a])
        is_go = (show == go_a) == (box == "🟩")
        ans = "👉 GO" if is_go else "✋ STOP"
        why = f"The box is {box} and you see {show}: " + ("GO." if is_go else "STOP.") + " Check the box colour first!"
        key = (go_a, box, show)
        show = f"{box} {show}"
    return item(gen_id("stopgo", level, *key), "Stop & go", level, rule + "  \nWhat do you do?",
                ["👉 GO", "✋ STOP"], ans, why, keep_order=True,
                html=f"<div style='font-size:5rem;text-align:center'>{show}</div>",
                hint="Stop, look, then think about the rule before you choose.")


ACTIONS = ["clap your hands 👏", "jump 🦘", "touch your nose 👃", "wave 👋", "sit down 🪑", "turn around 🔄",
           "stamp your feet 🦶", "raise your arms 🙌", "nod your head 🙂", "blink twice 👀", "touch your toes 🙇",
           "say hello 🗣️"]
ORD = ["first", "second", "third", "fourth"]


def _steps(level, rng, ctx):
    n = level + 1
    steps = rng.sample(ACTIONS, n + 1)
    steps, outsider = steps[:n], steps[n]
    memo = "First " + ", then ".join(steps) + "."
    kind = rng.choice(["nth", "after"] if level == 1 else ["nth", "after", "before"])
    if kind == "nth":
        k = rng.randrange(n)
        q, ans = f"What did you have to do **{ORD[k]}**?", steps[k]
    elif kind == "after":
        k = rng.randrange(n - 1)
        q, ans = f"What came right **after** '{steps[k]}'?", steps[k + 1]
    else:
        k = rng.randrange(1, n)
        q, ans = f"What came right **before** '{steps[k]}'?", steps[k - 1]
    choices = list(dict.fromkeys([ans] + [s for s in steps if s != ans][:2] + [outsider]))
    return item(gen_id("steps", kind, q, *steps), "Follow the steps", level, q, choices, ans,
                "The steps were: " + " → ".join(steps) + ".", memo=memo, say=memo,
                hint="Say the steps in your head, or count them on your fingers.")


_i = item
PLAN = [
    _i(201, "Plan & self-control", 1, "The teacher is talking and you know the answer. What can you do?",
       ["Raise your hand and wait", "Shout the answer", "Get up and walk to the board"], "Raise your hand and wait",
       "Raising your hand lets everyone have a turn, and the teacher will ask you."),
    _i(202, "Plan & self-control", 1, "It is {A}'s turn on the slide, and you want to go NOW. What can you do?",
       ["Wait and count to 10 in your head", "Push {A}", "Climb up the slide the wrong way"],
       "Wait and count to 10 in your head", "Counting makes waiting feel shorter. Your turn is coming!"),
    _i(203, "Plan & self-control", 1, "Your body feels wiggly and you can't sit still. What can you ask?",
       ["'Can I have a short movement break?'", "Run out of the classroom", "Kick the chair"],
       "'Can I have a short movement break?'", "Asking for a movement break is a smart choice. Moving helps focus."),
    _i(204, "Plan & self-control", 1, "You feel very angry. What can you do first?",
       ["Stop and take 3 deep breaths", "Throw something", "Shout at someone"], "Stop and take 3 deep breaths",
       "Stop, breathe, then think: that gives your brain time to choose."),
    _i(205, "Plan & self-control", 1, "You forgot what the teacher asked. What can you do?",
       ["Ask: 'Can you say it again, please?'", "Do something else", "Copy {A}"],
       "Ask: 'Can you say it again, please?'", "Asking again is always okay."),
    _i(206, "Plan & self-control", 1, "It is time to tidy up the toys. What helps?",
       ["Put the toys away one type at a time", "Hide them under the bed", "Leave and play outside"],
       "Put the toys away one type at a time", "Small steps make a big job easy: first cars, then blocks..."),
    _i(207, "Plan & self-control", 2, "Your homework has 10 questions and it feels too big. What is a good plan?",
       ["Do 3 questions, take a tiny break, then do 3 more", "Do all of them without a break", "Skip it"],
       "Do 3 questions, take a tiny break, then do 3 more", "Cutting a big job into small parts makes it easier."),
    _i(208, "Plan & self-control", 2, "The TV is on while you do homework, and you keep looking at it. What helps?",
       ["Turn it off or move to a quiet place", "Turn the volume up", "Watch and write at the same time"],
       "Turn it off or move to a quiet place", "Fewer distractions make it easier to focus."),
    _i(209, "Plan & self-control", 2, "You often forget your sports bag. What can help?",
       ["A checklist next to the door", "Hope you remember", "Never take a bag"], "A checklist next to the door",
       "A checklist remembers for you!"),
    _i(210, "Plan & self-control", 2, "{A} is telling a story and you want to talk too. What can you do?",
       ["Wait until {A} finishes, then talk", "Talk louder than {A}", "Walk away"],
       "Wait until {A} finishes, then talk", "Waiting for the end of the story shows {A} you are listening."),
    _i(211, "Plan & self-control", 2, "You have 15 minutes to get ready. What helps you not lose time?",
       ["A timer and a picture checklist", "Play first, then see", "Do everything at once"],
       "A timer and a picture checklist", "A timer shows the time passing, and the checklist shows what is left."),
    _i(212, "Plan & self-control", 2, "You want {A}'s pencil right now. What is a better choice?",
       ["Ask: 'Can I borrow your pencil, please?'", "Grab it", "Draw on {A}'s desk"],
       "Ask: 'Can I borrow your pencil, please?'", "Asking first is fair and kind."),
    _i(213, "Plan & self-control", 3, "You have a big project for Friday. What is the best first step?",
       ["Split it into small steps and plan one step each day", "Start on Friday morning", "Forget about it"],
       "Split it into small steps and plan one step each day", "A plan with small daily steps avoids last-minute stress."),
    _i(214, "Plan & self-control", 3, "You made a mistake in a game and want to quit. What can you tell yourself?",
       ["'Mistakes help me learn. I can try again.'", "'I am bad at everything.'", "'I will never play again.'"],
       "'Mistakes help me learn. I can try again.'", "Kind words to yourself help you keep going."),
    _i(215, "Plan & self-control", 3, "You are reading and your mind starts to wander. What can you do?",
       ["Notice it, then put your finger under the line and continue", "Close the book forever", "Read faster"],
       "Notice it, then put your finger under the line and continue",
       "Noticing is the first step. A finger or a ruler helps your eyes come back."),
    _i(216, "Plan & self-control", 3, "You want to play a game, but you have chores. What plan works best?",
       ["Chores first, then the game as a reward", "Game first, chores maybe later", "Do both at once"],
       "Chores first, then the game as a reward", "'First... then...' plans make the fun part a reward."),
    _i(217, "Plan & self-control", 3, "In a group game you want to change the rules right now. What can you do?",
       ["Suggest the idea calmly and let the group decide", "Change them without asking", "Stop the game"],
       "Suggest the idea calmly and let the group decide", "Sharing ideas calmly helps everyone keep playing."),
    _i(218, "Plan & self-control", 3, "You feel full of energy just before a test. What can help?",
       ["Stretch a little, then take slow breaths", "Run around the classroom", "Talk to everyone"],
       "Stretch a little, then take slow breaths", "A little movement and slow breathing help your body get ready."),
]

BANK = Bank(CATEGORIES, PLAN, {"Spot the target": _spot, "Same or different?": _same, "Stop & go": _stopgo,
                               "Follow the steps": _steps, "Robot rescue": g.robot, "Detective": g.detective,
                               "Pack your school bag": g.school_bag, "Emotion detective": g.emotions,
                               "Treasure map": g.treasure, "Copy the rhythm": g.rhythm})


def pick_item(df_act, cap=3, category=None, rng=random, recent=()):
    return BANK.pick(df_act, cap, category, rng, recent)


def movement(rng=random):
    return rng.choice(MOVES)
