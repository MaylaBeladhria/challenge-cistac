"""Task registry.

Every cognitive dimension is a small function registered with @register.
A generator receives (level 1-5, rng) and returns a dict with:
  prompt, choices, answer, hint, tlimit (seconds)   [+ optional: html, memorize, show_s]
To add a dimension (e.g. during the 'surprise element'), see tasks_custom.py: ~15 lines.
"""

COLORS = {"red": "#e53935", "blue": "#1e88e5", "green": "#43a047", "orange": "#fb8c00"}

REGISTRY = {}


def register(name, description, chance=0.25):
    """chance = probability of a correct answer by guessing (1 / number of choices)."""
    def deco(fn):
        REGISTRY[name] = dict(desc=description, chance=chance, fn=fn)
        return fn
    return deco


def pick_choices(ans, distractors, rng):
    ch = [ans] + [d for d in dict.fromkeys(distractors) if d != ans][:3]
    rng.shuffle(ch)
    return ch


@register("Working memory", "Hold and manipulate information for a few seconds.")
def working_memory(level, rng):
    n = 2 + level
    seq = [rng.randint(0, 9) for _ in range(n)]
    back = level >= 3
    ans = "".join(map(str, seq[::-1] if back else seq))
    wrong = set()
    while len(wrong) < 3:
        l = list(ans)
        i = rng.randrange(n)
        l[i] = str((int(l[i]) + rng.randint(1, 9)) % 10)
        w = "".join(l)
        if w != ans:
            wrong.add(w)
    return dict(prompt="Which option is the sequence " + ("BACKWARDS?" if back else "in the SAME order?"),
                memorize=" ".join(map(str, seq)), show_s=0.7 * n, tlimit=15.0,
                choices=pick_choices(ans, sorted(wrong), rng), answer=ans,
                hint="Group the digits in chunks of 2-3 to remember them.")


@register("Attention", "Focus on relevant information and ignore distractions.")
def attention(level, rng):  # Stroop task
    names = list(COLORS)
    word = rng.choice(names)
    p_cong = [0.8, 0.6, 0.4, 0.2, 0.0][level - 1]
    ink = word if rng.random() < p_cong else rng.choice([c for c in names if c != word])
    ch = names[:]
    rng.shuffle(ch)
    return dict(prompt="What is the INK colour of the word? (ignore what it says)",
                html=f"<h1 style='color:{COLORS[ink]};text-align:center'>{word.upper()}</h1>",
                tlimit=max(2.5, 6 - 0.6 * level), choices=ch, answer=ink,
                hint="Look at the colour only, not at the letters.")


@register("Processing speed", "Perform simple operations quickly and accurately.")
def processing_speed(level, rng):
    hi = [9, 15, 25, 40, 60][level - 1]
    a, b = rng.randint(2, hi), rng.randint(2, hi)
    op = rng.choice("+-")
    ans = a + b if op == "+" else a - b
    dist = [ans + k for k in (-10, -1, 1, 10, 2, -2)]
    rng.shuffle(dist)
    return dict(prompt=f"Compute: {a} {op} {b}", tlimit=max(3.0, 9 - level),
                choices=pick_choices(ans, dist, rng), answer=ans,
                hint="Round one number to the nearest ten, then adjust.")


@register("Logical reasoning", "Detect rules and patterns to predict what comes next.")
def logical_reasoning(level, rng):
    if level == 1:
        a, d = rng.randint(1, 20), rng.randint(2, 7)
        s = [a + i * d for i in range(6)]
    elif level == 2:
        a, r = rng.randint(1, 4), rng.choice([2, 3])
        s = [a * r ** i for i in range(6)]
    elif level == 3:
        a, x, y = rng.randint(5, 20), rng.randint(2, 9), rng.randint(-5, -1)
        s = [a]
        for i in range(5):
            s.append(s[-1] + (x if i % 2 == 0 else y))
    elif level == 4:
        s = [rng.randint(1, 5), rng.randint(1, 5)]
        while len(s) < 6:
            s.append(s[-1] + s[-2])
    else:
        a, b = rng.randint(1, 10), rng.randint(1, 10)
        da, db = rng.randint(2, 5), rng.randint(3, 7)
        s = [a, b, a + da, b + db, a + 2 * da, b + 2 * db]
    ans = s[5]
    dist = [ans + k for k in (-3, -2, -1, 1, 2, 3)]
    rng.shuffle(dist)
    return dict(prompt="Which number comes next?  " + ", ".join(map(str, s[:5])) + ", ?",
                tlimit=30.0, choices=pick_choices(ans, dist, rng), answer=ans,
                hint="Look at the difference or ratio between neighbouring numbers.")


@register("Mental flexibility", "Switch between rules without losing accuracy.", chance=0.5)
def mental_flexibility(level, rng):  # colour-cued rule switching
    cues = ["BLUE", "ORANGE"] + (["GREEN"] if level >= 3 else [])
    cue = rng.choice(cues)
    while True:
        a, b = rng.sample(range(10, 99), 2)
        if cue != "GREEN" or (a % 2) != (b % 2):
            break
    ans = {"BLUE": max(a, b), "ORANGE": min(a, b), "GREEN": a if a % 2 == 0 else b}[cue]
    col = {"BLUE": COLORS["blue"], "ORANGE": COLORS["orange"], "GREEN": COLORS["green"]}[cue]
    return dict(prompt="Apply the rule of the colour: BLUE = larger number, ORANGE = smaller number"
                       + (", GREEN = even number." if level >= 3 else "."),
                html=f"<h1 style='color:{col};text-align:center'>{cue} &nbsp; ({a} / {b})</h1>",
                tlimit=max(3.0, 9 - level), choices=[str(a), str(b)], answer=str(ans),
                hint="Identify the colour first, then apply its rule.")
