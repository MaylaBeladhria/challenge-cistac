"""Dyslexia profile, final version: the 12 games of "Jeux interactifs pour les enfants dyslexiques".

QUESTION GAMES (added to the 🔤 Word games bank, literacy.py):
  Sound detective · Twin words · Hidden letters · Word market · Meaning hunt · Prefixes & suffixes ·
  Story in pictures (levels 1-2) · upgraded: Syllable train, Rhyme maze (level 3: tick ALL the rhymes)
INTERACTIVE GAMES (tab "🧱 Build & read", app.py):
  Build the word (letter tiles) · Sentence puzzle (word cards) · Magic echo (words light up while read aloud) ·
  My story in pictures (order pictures, fill in, then write my own story)
Rules from the document: listen as many times as needed, speed is never the goal, confusing b/d is never
treated as a shameful mistake, several ways to answer (pick, tap, type).
"""
import json

from practice import gen_id, item

# ================================================================= Sound detective (phonological awareness)
ONSETS = {"s": ["☀️ sun", "🧦 sock", "🐍 snake", "🧂 salt"], "m": ["🗺️ map", "🌙 moon", "🥛 milk", "🐭 mouse"],
          "b": ["🚌 bus", "🛏️ bed", "⚽ ball", "🍌 banana"], "d": ["🐶 dog", "🦆 duck", "🦌 deer", "🥁 drum"],
          "f": ["🐟 fish", "🦊 fox", "🪭 fan", "🐸 frog"], "p": ["🐷 pig", "🖊️ pen", "🍕 pizza", "🥧 pie"],
          "sh": ["🚢 ship", "🏪 shop", "🐚 shell", "🐑 sheep"], "ch": ["🍟 chips", "🪑 chair", "🧀 cheese",
                                                                      "🐔 chicken"]}
FAR = {"s": ["m", "b", "d", "f", "p"], "m": ["s", "f", "sh", "ch"], "b": ["s", "m", "f", "sh"],
       "d": ["s", "m", "f", "sh"], "f": ["m", "b", "d", "ch"], "p": ["s", "m", "sh"], "sh": ["m", "b", "d", "p"],
       "ch": ["s", "m", "f", "b"]}
ENDS = {"g": ["🐶 dog", "🐷 pig", "👜 bag", "🪵 log"], "t": ["🐱 cat", "🎩 hat", "🦇 bat", "🍲 pot"],
        "n": ["☀️ sun", "🖊️ pen", "🔟 ten", "🗑️ bin"], "p": ["☕ cup", "🗺️ map", "🧢 cap", "🔝 top"],
        "sh": ["🐟 fish", "🍽️ dish", "🌠 wish", "🖌️ brush"]}
MIDDLE = {"a": ["🐱 cat", "🗺️ map", "👜 bag"], "o": ["🐶 dog", "🍲 pot", "🦊 fox"], "i": ["🐷 pig", "🗑️ bin", "🐟 fish"],
          "u": ["☀️ sun", "☕ cup", "🚌 bus"], "e": ["🛏️ bed", "🖊️ pen", "🔟 ten"]}
PAIRS = [("cat", "cap", "last"), ("cat", "bat", "first"), ("cat", "cot", "middle"), ("pig", "big", "first"),
         ("pig", "peg", "middle"), ("pin", "pit", "last"), ("sun", "bun", "first"), ("dog", "dig", "middle"),
         ("bed", "bet", "last"), ("ship", "shop", "middle"), ("fish", "dish", "first"), ("map", "mop", "middle"),
         ("hat", "ham", "last"), ("pan", "fan", "first"), ("hop", "hot", "last")]
POS = {"first": "🥇 the first sound", "middle": "🥈 the middle sound", "last": "🥉 the last sound"}


def _w(x):
    return x.split(" ", 1)[1]


def sound_detective(level, rng, ctx):
    cat = "Sound detective"
    praise = "Well done! You listened carefully to the sounds. 👂"
    if level == 1:
        snd = rng.choice(list(ONSETS))
        ans = rng.choice(ONSETS[snd])
        others = [rng.choice(ONSETS[o]) for o in rng.sample(FAR[snd], 2)]
        ch = [ans] + others
        return item(gen_id("snd1", snd, ans, *others), cat, level, f"🔊 Which word **starts** with the sound /{snd}/?",
                    ch, ans, f"'{_w(ans)}' starts with /{snd}/.", say=f"Which word starts with {snd}? "
                    + ", ".join(_w(c) for c in ch), praise=praise)
    if level == 2:
        if rng.random() < 0.5:
            snd = rng.choice(list(ENDS))
            ans = rng.choice(ENDS[snd])
            others = [rng.choice(ENDS[o]) for o in rng.sample([e for e in ENDS if e != snd], 2)]
            where = "ends with"
        else:
            snd = rng.choice(list(MIDDLE))
            ans = rng.choice(MIDDLE[snd])
            others = [rng.choice(MIDDLE[o]) for o in rng.sample([e for e in MIDDLE if e != snd], 2)]
            where = "has in the middle"
        ch = [ans] + others
        return item(gen_id("snd2", where, ans, *others), cat, level, f"🔊 Which word **{where}** the sound /{snd}/?",
                    ch, ans, f"'{_w(ans)}' {where} /{snd}/.", say=" , ".join(_w(c) for c in ch), praise=praise,
                    hint="Say each word very slowly, like a robot: c... a... t.")
    a, b, pos = rng.choice(PAIRS)
    return item(gen_id("snd3", a, b), cat, level, f"🔊 Listen: **{a}** ➜ **{b}**. Which sound changed?",
                list(POS.values()), POS[pos], f"'{a}' and '{b}': only {POS[pos].split(' ', 1)[1]} changed.",
                say=f"{a}. {b}.", keep_order=True, praise="Great ears! You found the sound that changed. 👂")


# ================================================================= Twin words (almost the same)
TWINS = [("ship", "sheep"), ("pat", "bat"), ("bed", "bad"), ("pin", "pen"), ("cap", "cup"), ("dog", "dig"),
         ("sock", "sack"), ("three", "tree"), ("fan", "van"), ("coat", "goat"), ("bear", "pear"), ("mouse", "house"),
         ("cat", "cut"), ("big", "dig"), ("pig", "big"), ("hat", "hot"), ("sun", "son"), ("fox", "box")]
CLOSE_SETS = [["ship", "sheep", "shop", "chip"], ["bed", "bad", "bid", "bud"], ["pin", "pen", "pan", "bin"],
              ["cap", "cup", "cop", "map"], ["dog", "dig", "dug", "bog"], ["hat", "hot", "hit", "hut"]]


def twin_words(level, rng, ctx):
    cat = "Twin words"
    praise = "You spotted what changes between the two words! 🔍"
    if level == 1:
        a, b = rng.choice(TWINS)
        far = rng.choice([w for p in TWINS for w in p if w[0] != a[0] and len(w) != len(a)] or ["umbrella"])
        return item(gen_id("twin1", a, far), cat, level, "🔊 Listen to the word. Which one is it?", [a, far], a,
                    f"The word was '{a}'. You can listen again as many times as you like.", say=a, praise=praise)
    if level == 2:
        a, b = rng.choice(TWINS)
        if len(a) != len(b):
            where = "a letter was added or changed in the middle"
        else:
            k = next(i for i in range(len(a)) if a[i] != b[i])
            where = "the first letter" if k == 0 else "the last letter" if k == len(a) - 1 else "a middle letter"
        ch = ["the first letter", "a middle letter", "the last letter"]
        if where not in ch:
            ch = ch[:2] + [where]
        html = (f"<div style='text-align:center;font-size:2.4rem;letter-spacing:.12em'>{a} &nbsp;/&nbsp; {b}</div>")
        return item(gen_id("twin2", a, b), cat, level, f"Look and listen: **{a}** / **{b}**. What is different?", ch,
                    where, f"'{a}' and '{b}' differ by {where}.", html=html, say=f"{a}. {b}.", keep_order=True,
                    praise=praise)
    grp = rng.choice(CLOSE_SETS)
    w = rng.choice(grp)
    return item(gen_id("twin3", w, *grp), cat, level, "🔊 Listen (again if you like). Which word did you hear?",
                grp, w, f"You heard '{w}'. These words look and sound very close: well done for listening "
                "carefully.", say=w, praise=praise, hint="Listen to the middle sound: is it a, e, i, o or u?")


# ================================================================= Hidden letters (b / d / p / q)
FAR_LETTERS = ["x", "o", "s", "m", "k", "z", "t", "h"]
MIRROR = {"b": ["d", "p"], "d": ["b", "q"], "p": ["q", "b"], "q": ["p", "d"]}
B_WORDS = {"b": ["bed", "bus", "bag", "web", "tub", "crab"], "d": ["dog", "bed", "sad", "dig", "red", "duck"],
           "p": ["pig", "cup", "map", "pen", "top", "ship"]}
NO_WORDS = {"b": ["dog", "pig", "sun", "dad", "cup", "pod"], "d": ["bus", "pig", "cup", "top", "web", "bag"],
            "p": ["bed", "dog", "bus", "dad", "bag", "tub"]}
TIPS = {"b": "b: the bat | comes first, then the ball o.", "d": "d: the drum o comes first, then the stick |.",
        "p": "p: the stick goes down, the ball is at the top.", "q": "q: like p in a mirror, with the stick on the right."}


def hidden_letters(level, rng, ctx):
    cat = "Hidden letters"
    praise = "You took the time to look at the shape of each letter. 🔎"
    t = rng.choice(["b", "d", "p"] if level < 3 else ["b", "d", "p"])
    if level < 3:
        n = rng.randint(2, 5)
        others = FAR_LETTERS if level == 1 else MIRROR[t] + rng.sample(FAR_LETTERS, 1)
        cells = [t] * n + [rng.choice(others) for _ in range(16 - n)]
        rng.shuffle(cells)
        grid = "<br>".join(" ".join(cells[i:i + 4]) for i in range(0, 16, 4))
        html = ("<div style='text-align:center'><div style='font-size:1.1rem'>📚 In the library...</div>"
                "<div style='display:inline-block;font-family:Lexend,Verdana,sans-serif;font-size:2.4rem;"
                "letter-spacing:.6em;line-height:1.5;padding:.6rem 1rem;border-radius:12px;background:#fff8e1'>"
                + grid + "</div></div>")
        aid = f"  \n💡 {TIPS[t]}" if level == 2 else ""
        return item(gen_id("let", level, *cells), cat, level,
                    f"Find every letter **{t}**" + (f" (do not count {' or '.join(MIRROR[t])})" if level == 2 else "")
                    + f". How many **{t}** are there?{aid}", sorted({n - 1, n, n + 1, n + 2}), n,
                    f"There are {n} letters {t}. {TIPS[t]}", html=html, keep_order=True, praise=praise,
                    hint="Point at each letter, one row at a time.")
    yes = rng.sample(B_WORDS[t], 3)
    no = rng.sample([w for w in NO_WORDS[t] if t not in w], 3)
    return item(gen_id("let3", t, *yes, *no), cat, level, f"Tick the words that have the letter **{t}** in them.",
                yes + no, " + ".join(yes), f"Words with {t}: {', '.join(yes)}. {TIPS[t]}", multi=True, answers=yes,
                praise=praise)


# ================================================================= Word market (sort words in boxes)
RULE_SETS = {"end -ake": ["cake", "lake", "make", "snake", "bake"], "end -ine": ["line", "nine", "pine", "mine"],
             "end -ug": ["bug", "mug", "rug", "hug"], "end -ot": ["hot", "pot", "dot", "lot"],
             "start s": ["sun", "sock", "sit", "sad"], "start m": ["map", "moon", "milk", "mat"],
             "sound ee": ["tree", "bee", "see", "feet"], "sound oo": ["moon", "spoon", "food", "boot"]}


def _rule_txt(r):
    kind, v = r.split(" ")
    return {"end": f"words ending with {v}", "start": f"words starting with {v}", "sound": f"words with '{v}'"}[kind]


def word_market(level, rng, ctx):
    cat = "Word market"
    praise = "You found a rule that helps organise words! 🧺"
    if level == 1:
        rules = rng.sample([r for r in RULE_SETS if r.startswith("end")], 3)
    elif level == 2:
        rules = [rng.choice([r for r in RULE_SETS if r.startswith("end")]),
                 rng.choice([r for r in RULE_SETS if not r.startswith("end")])]
    else:
        r = rng.choice(list(RULE_SETS))
        words = rng.sample(RULE_SETS[r], 3)
        other = rng.sample([x for x in RULE_SETS if x != r and x.split()[0] != r.split()[0]], 2)
        ch = [_rule_txt(r)] + [_rule_txt(o) for o in other]
        return item(gen_id("mkt3", r, *words), cat, level,
                    f"🧺 The seller put these words in one box: **{', '.join(words)}**. What is the rule?",
                    ch, ch[0], f"They are all {ch[0]}.", praise=praise,
                    hint="Look at the beginning, then the end of each word. What is the same?")
    word = None
    for _ in range(50):
        r = rng.choice(rules)
        w = rng.choice(RULE_SETS[r])
        if sum(w in RULE_SETS[x] for x in rules) == 1:  # the word fits exactly one box
            word = w
            break
    boxes = [f"📦 {_rule_txt(x)}" for x in rules]
    ans = f"📦 {_rule_txt(r)}"
    return item(gen_id("mkt", level, word, *rules), cat, level,
                f"🧺 Help the seller! Which box does the word **{word}** go in?", boxes, ans,
                f"'{word}' goes with the {_rule_txt(r)}.", say=word, keep_order=True, praise=praise,
                hint="Example: 'cake' and 'lake' both end with -ake, so they share a box.")


# ================================================================= Meaning hunt (reading comprehension)
NEEDS = [("takes an umbrella", "it is raining", "☂️ an umbrella", ["🕶️ sunglasses", "🩱 a swimsuit"]),
         ("puts on a warm coat", "it is very cold", "🧥 a warm coat", ["🩳 shorts", "🧢 a cap"]),
         ("drinks some water", "{A} is thirsty", "💧 water", ["🍪 a biscuit", "🛏️ a bed"]),
         ("takes a torch", "it is dark", "🔦 a torch", ["⚽ a ball", "🖍️ a crayon"]),
         ("puts on sun cream", "the sun is hot", "🧴 sun cream", ["🧤 gloves", "☂️ an umbrella"])]
PLACES = ["🏞️ the park", "🏖️ the beach", "🏫 the school yard", "🌳 the forest"]
COLOURS = ["red", "blue", "green", "yellow"]
FOODS = ["🍎 apples", "🍌 bananas", "🥪 sandwiches", "🍪 biscuits"]
IMPLICIT = [("{A} puts on a coat, a hat and gloves. Outside, everything is white.", "What is the weather like?",
             "❄️ Cold and snowy", ["☀️ Hot and sunny", "🌧️ Warm and rainy"]),
            ("{A} yawns, puts on pyjamas and turns off the light.", "What is {A} going to do?",
             "😴 Go to sleep", ["🏫 Go to school", "⚽ Play football"]),
            ("{A} blows out the candles and everybody sings.", "What day is it for {A}?",
             "🎂 A birthday", ["🦷 A dentist day", "🧹 A cleaning day"]),
            ("{A} looks everywhere: under the bed, in the bag, in the car. Then {A} smiles.",
             "What happened?", "🔎 {A} found something", ["😴 {A} fell asleep", "🍕 {A} ate pizza"]),
            ("{A}'s plate is empty and {A} says: 'Can I have more, please?'", "How was the food?",
             "😋 {A} liked it", ["🤢 {A} hated it", "🥶 It was frozen"])]


def meaning_hunt(level, rng, ctx):
    cat = "Meaning hunt"
    praise = "You found the important information in the story! 📖"
    if level == 1:
        k = rng.randrange(len(NEEDS))
        act, why, ans, dist = NEEDS[k]
        text = f"{{A}} {act} because {why}."
        return item(gen_id("mean1", k), cat, level, f"📖 *{text}*  \nWhat does {{A}} need?", [ans] + dist, ans,
                    f"The story says: '{text}'", say=text, praise=praise)
    if level == 2:
        place, col, food = rng.choice(PLACES), rng.choice(COLOURS), rng.choice(FOODS)
        text = (f"{{A}} goes to {place.split(' ', 1)[1]} with {{B}}. They play with a {col} ball. "
                f"Then they eat {food.split(' ', 1)[1]}. In the end, they go home happy.")
        q = rng.choice(["colour", "food", "place"])
        if q == "colour":
            question, ans, ch = "What colour is the ball?", col, rng.sample([c for c in COLOURS if c != col], 2)
        elif q == "food":
            question, ans, ch = "What do they eat?", food, rng.sample([f for f in FOODS if f != food], 2)
        else:
            question, ans, ch = "Where do they go?", place, rng.sample([p for p in PLACES if p != place], 2)
        return item(gen_id("mean2", place, col, food, q), cat, level, f"📖 *{text}*  \n**{question}**",
                    [ans] + ch, ans, f"The story says it: look for the {q}.", say=text, praise=praise,
                    hint="Read (or listen to) the story again and look for the word that answers the question.")
    k = rng.randrange(len(IMPLICIT))
    text, question, ans, dist = IMPLICIT[k]
    return item(gen_id("mean3", k), cat, level, f"📖 *{text}*  \n**{question}**", [ans] + dist, ans,
                "The story does not say it directly: the clues help you guess.", say=text, praise=praise,
                hint="The answer is not written: look for clues in the story.")


# ================================================================= Prefixes & suffixes
WEATHER = [("rainy", "🌧️"), ("sunny", "☀️"), ("snowy", "❄️"), ("windy", "🌬️"), ("cloudy", "☁️")]
OPPOSITES = [("happy", "😀", "unhappy", "😞"), ("lock", "🔒", "unlock", "🔓"), ("tidy", "🧹✨", "untidy", "🧦🧸📚")]
AFFIX = [("help", "-ful", "full of help", "helpful"), ("care", "-ful", "full of care", "careful"),
         ("play", "re-", "play again", "replay"), ("read", "re-", "read again", "reread"),
         ("kind", "un-", "not kind", "unkind"), ("happy", "un-", "not happy", "unhappy"),
         ("fear", "-less", "without fear", "fearless"), ("teach", "-er", "a person who teaches", "teacher"),
         ("paint", "-er", "a person who paints", "painter"), ("slow", "-ly", "in a slow way", "slowly")]
USE = [("Please be ___ with the glass: it can break.", "careful", ["careless", "carefully"]),
       ("The ___ wrote the date on the board.", "teacher", ["teach", "teaching"]),
       ("The tortoise walks very ___.", "slowly", ["slow", "slowness"]),
       ("My friend was very ___: she helped me carry my bag.", "helpful", ["helpless", "help"]),
       ("The film was so good that I want to ___ it.", "rewatch", ["unwatch", "watcher"]),
       ("It is ___ to pull a cat's tail.", "unkind", ["kindly", "kindness"]),
       ("Take your umbrella: it is ___ today.", "rainy", ["rainless", "rainer"])]


def affixes(level, rng, ctx):
    cat = "Prefixes & suffixes"
    praise = "You discovered how a small part changes the meaning of a word! 🧩"
    if level == 1:
        if rng.random() < 0.5:
            w, e = rng.choice(WEATHER)
            others = [x for x in WEATHER if x[0] != w]
            ch = [e] + [o[1] for o in rng.sample(others, 2)]
            return item(gen_id("aff1w", w), cat, level, f"Which picture shows **{w}**?", ch, e,
                        f"{w} = {w[:-1] if w != 'sunny' else 'sun'} + y {e}.", say=w, praise=praise)
        base, be, neg, ne = rng.choice(OPPOSITES)
        return item(gen_id("aff1u", neg), cat, level, f"Which picture shows **{neg}**?", [ne, be], ne,
                    f"un- means 'not' or 'the opposite': {neg} is the opposite of {base}.", say=neg, praise=praise)
    if level == 2:
        base, aff, meaning, word = rng.choice(AFFIX)
        ch = list(dict.fromkeys([aff] + rng.sample(["-ful", "re-", "un-", "-less", "-er", "-ly"], 4)))[:3]
        if aff not in ch:
            ch[-1] = aff
        return item(gen_id("aff2", base, aff), cat, level,
                    f"**{base}** + ? = *{meaning}*. Which small part do you add?", ch, aff,
                    f"{base} + {aff} = {word} ({meaning}).", praise=praise,
                    hint="re- = again · un- = not · -ful = full of · -less = without · -er = a person who · -ly = in a ... way")
    sent, ans, dist = rng.choice(USE)
    return item(gen_id("aff3", sent), cat, level, f"Choose the word that fits: *{sent}*", [ans] + dist, ans,
                f"'{sent.replace('___', ans)}'", say=sent.replace("___", "blank"), praise=praise)


# ================================================================= Story in pictures
STORIES = [
    (["👧", "🔑", "🚪"], ["girl", "key", "door"], ["The girl finds a key.", "She walks to the door.",
                                                  "She opens the door."]),
    (["🐶", "⚽", "🌳"], ["dog", "ball", "park"], ["The dog sees a ball.", "He runs after the ball.",
                                                  "He plays in the park."]),
    (["👦", "🌧️", "☂️"], ["boy", "rain", "umbrella"], ["The boy goes out.", "It starts to rain.",
                                                       "He opens his umbrella."]),
    (["🌱", "💧", "🌻"], ["seed", "water", "flower"], ["Mia plants a seed.", "She gives it water.",
                                                      "A big flower grows."]),
    (["🥚", "🐣", "🐔"], ["egg", "chick", "hen"], ["There is an egg.", "A little chick comes out.",
                                                  "The chick grows into a hen."]),
    (["🍞", "🧈", "🥪"], ["bread", "butter", "sandwich"], ["Tom takes some bread.", "He adds butter.",
                                                          "He eats his sandwich."]),
]


def story_pictures(level, rng, ctx):
    cat = "Story in pictures"
    praise = "You built a story! You can make it better step by step. 📚"
    k = rng.randrange(len(STORIES))
    pics, words, sents = STORIES[k]
    if level == 1:
        right = " ➜ ".join(pics)
        wrong = set()
        while len(wrong) < 2:
            p = pics[:]
            rng.shuffle(p)
            if p != pics:
                wrong.add(" ➜ ".join(p))
        return item(gen_id("story1", k), cat, level, "Put the pictures in order. Which order tells the story?",
                    [right] + sorted(wrong), right, " ".join(sents), say=" ".join(sents), praise=praise)
    j = rng.randrange(3)
    target = words[j]
    sentence = sents[j]
    blanked = sentence.replace(target, "___", 1) if target in sentence else None
    if blanked is None:
        j, target = 0, words[0]
        blanked = sents[0].replace(target, "___", 1)
        sentence = sents[0]
    bank = [target] + [w for w in words if w != target][:2] + ([rng.choice(["cat", "car", "moon"])] if level == 3 else [])
    return item(gen_id("story", level, k, j), cat, level,
                f"{' ➜ '.join(pics)}  \nComplete with the word bank: *{blanked}*", bank, target,
                f"'{sentence}'", say=" ".join(sents), praise=praise,
                hint="Look at the pictures: which one matches this sentence?")


# ================================================================= interactive data (tab "Build & read")
# words cut into tiles (one tile = one sound, sometimes written with 2 or 3 letters)
BUILD = {1: [("☀️", "sun", ["s", "u", "n"]), ("🐱", "cat", ["c", "a", "t"]), ("🐶", "dog", ["d", "o", "g"]),
             ("🚌", "bus", ["b", "u", "s"]), ("🐷", "pig", ["p", "i", "g"]), ("🎩", "hat", ["h", "a", "t"]),
             ("🛏️", "bed", ["b", "e", "d"]), ("🦊", "fox", ["f", "o", "x"]), ("🖊️", "pen", ["p", "e", "n"]),
             ("🗺️", "map", ["m", "a", "p"])],
         2: [("🚢", "ship", ["sh", "i", "p"]), ("🐟", "fish", ["f", "i", "sh"]), ("🏪", "shop", ["sh", "o", "p"]),
             ("🍟", "chip", ["ch", "i", "p"]), ("🦆", "duck", ["d", "u", "ck"]), ("🧦", "sock", ["s", "o", "ck"]),
             ("🌙", "moon", ["m", "oo", "n"]), ("🐝", "bee", ["b", "ee"]), ("🐑", "sheep", ["sh", "ee", "p"]),
             ("🦷", "teeth", ["t", "ee", "th"])],
         3: [("💡", "light", ["l", "igh", "t"]), ("🚀", "rocket", ["r", "o", "ck", "e", "t"]),
             ("🌈", "rainbow", ["r", "ai", "n", "b", "ow"]), ("🥄", "spoon", ["s", "p", "oo", "n"]),
             ("🐔", "chicken", ["ch", "i", "ck", "e", "n"]), ("🐬", "dolphin", ["d", "o", "l", "ph", "i", "n"]),
             ("🥕", "carrot", ["c", "a", "rr", "o", "t"]), ("🏰", "castle", ["c", "a", "s", "t", "le"]),
             ("🐘", "elephant", ["e", "l", "e", "ph", "a", "n", "t"]), ("🌳", "garden", ["g", "ar", "d", "e", "n"])]}
SOUND_OF = {"a": "a, as in apple", "b": "b, as in bat", "c": "c, as in cat", "d": "d, as in dog", "e": "e, as in egg",
            "f": "f, as in fish", "g": "g, as in goat", "h": "h, as in hat", "i": "i, as in insect",
            "l": "l, as in lion", "m": "m, as in moon", "n": "n, as in nose", "o": "o, as in octopus",
            "p": "p, as in pig", "r": "r, as in rabbit", "s": "s, as in sun", "t": "t, as in tap",
            "u": "u, as in umbrella", "x": "x, as in box", "sh": "sh, as in ship", "ch": "ch, as in chip",
            "ck": "ck, as in duck", "oo": "oo, as in moon", "ee": "ee, as in bee", "th": "th, as in teeth",
            "igh": "igh, as in light", "ai": "ai, as in rain", "ow": "ow, as in snow", "ph": "ph, as in phone",
            "rr": "rr, as in carrot", "le": "le, as in castle", "ar": "ar, as in car"}
DISTRACT = {"b": "d", "d": "b", "p": "q", "n": "u", "m": "w", "sh": "ch", "ch": "sh", "ee": "ea", "oo": "o"}

SENTENCE_CARDS = {1: [["The cat", "is sleeping", "on the sofa."], ["My dog", "likes", "big bones."],
                      ["The sun", "is", "very hot."], ["We", "eat", "red apples."], ["Mia", "reads", "a book."]],
                  2: [["The little bird", "sings", "a song", "in the tree."],
                      ["My brother", "plays", "football", "after school."],
                      ["The children", "build", "a sandcastle", "on the beach."],
                      ["Grandma", "bakes", "a cake", "on Sunday."]],
                  3: [["I take", "my coat", "because", "it is", "cold outside."],
                      ["We went", "to the park", "and then", "we had", "an ice cream."],
                      ["The dog", "was tired,", "so", "he slept", "in his basket."],
                      ["Tom wanted", "to play,", "but", "it was", "time for bed."]]}
SENTENCE_PICS = {"The cat": "🐱🛋️", "My dog": "🐶🦴", "The sun": "☀️🔥", "We": "🍎", "Mia": "👧📖",
                 "The little bird": "🐦🌳", "My brother": "👦⚽", "The children": "🧒🏖️", "Grandma": "👵🎂"}

ECHO = {1: ["The little dog runs home.", "I can see a red bus.", "The cat is on the bed.", "We like to play."],
        2: ["The happy children play in the big green park.", "My friend has a blue kite with a long tail.",
            "After lunch, we read a story about a dragon."],
        3: ["Sam opens the door. The garden is full of snow! He puts on his boots, his hat and his gloves. "
            "Then he runs outside to build a snowman.",
            "It is Saturday. Lina and her dad go to the market. They buy apples, bread and cheese. "
            "Lina carries the bag all the way home."]}


def echo_html(text, rate=0.8):
    """Words light up one by one while the browser voice reads the sentence. Replay without limit."""
    words = text.split()
    spans = " ".join(f"<span id='w{i}' style='padding:.05em .15em;border-radius:6px'>{w}</span>"
                     for i, w in enumerate(words))
    return f"""<div style="font-family:Lexend,Verdana,sans-serif;padding:.6rem">
<div id="t" style="font-size:1.7rem;line-height:2.1;letter-spacing:.04em">{spans}</div>
<div style="margin-top:.6rem;font-family:sans-serif">
<button id="go" style="font-size:1.05rem;padding:.35rem 1rem;border-radius:10px;border:1px solid #888">🔊 Listen</button>
&nbsp; 🐢 <input id="r" type="range" min="0.5" max="1.1" step="0.1" value="{rate}"> 🐇</div></div>
<script>
const W = {json.dumps(words)};
let timer=null;
function mark(i){{ W.forEach((_,k)=>{{ const e=document.getElementById('w'+k);
  e.style.background = k===i ? '#ffe082' : (k<i ? '#e8f5e9' : 'transparent'); }}); }}
document.getElementById('go').onclick = () => {{
  speechSynthesis.cancel(); clearInterval(timer);
  const rate = +document.getElementById('r').value;
  const u = new SpeechSynthesisUtterance(W.join(' ')); u.lang='en-US'; u.rate=rate;
  let i=0, gotBoundary=false; mark(0);
  u.onboundary = e => {{ if(e.name && e.name!=='word') return; gotBoundary=true;
    const before = W.join(' ').slice(0, e.charIndex).split(' ').filter(Boolean).length; mark(before); }};
  u.onend = () => {{ clearInterval(timer); mark(W.length); }};
  // fallback when the voice gives no word boundaries: light the words at a steady pace
  timer = setInterval(() => {{ if(!gotBoundary){{ i++; mark(Math.min(i, W.length-1)); }} }}, 420/rate);
  speechSynthesis.speak(u);
}};
</script>"""
