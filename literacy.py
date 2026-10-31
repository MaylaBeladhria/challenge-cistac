"""Writing practice and word games (dyslexia profile, original content, English).

WRITING PRACTICE ("look, hide, write")
  The child looks at a sentence, hides it, then writes it from memory. Two other modes: copy (the sentence stays
  visible) and listen & write (dictation by the browser voice). `compare_writing` checks the result:
    - word by word (missing, extra and misspelled words),
    - letter by letter inside each misspelled word (which letters are wrong or missing),
    - the kind of slip (mirror letters b/d p/q, swapped letters, missing / extra letter, double letter, vowel),
      each with a short, friendly tip,
    - capital letter and final full stop are checked separately and never lower the score.
  Misspelled words become the child's "tricky words" and come back in the spelling game.

WORD GAMES (all generated, so they keep changing)
  Spelling       hear a word, pick the right spelling among look-alikes (uses the child's tricky words first)
  Syllables      clap the beats of a word
  Rhymes         find the word that rhymes (level 3: the one that does NOT rhyme)
  Word order     put the mixed-up words of a sentence in the right order
Practice only: nothing here measures or labels a reading difficulty.
"""
import difflib
import random
import re
from collections import Counter

from practice import Bank, gen_id, item

# ------------------------------------------------------------------ writing sentences (level 1 = shortest)
WRITING_TEXTS = {
    1: ["I see a cat.", "The dog is big.", "We can run.", "My hat is red.", "A bug is on the bed.",
        "Mum has a pen.", "The sun is up.", "Dad can fix it.", "The fox sat down.", "We dig in the mud.",
        "It is a hot day.", "I got a pet."],
    2: ["The fish swims in the pond.", "I can ride my bike.", "She has a green kite.", "We play ball in the park.",
        "The frog jumps on a log.", "My dad drinks hot milk.", "The bird is in the tree.", "Look at the big ship.",
        "The duck is quick.", "I like to read books.", "The cake is on the plate."],
    3: ["The children played with a bright yellow ball.", "My brother brushed his teeth before bed.",
        "We watched the rain from the window.", "The queen wore a shiny crown.",
        "Please shut the door when you leave.", "Our teacher drew a circle on the board.",
        "The phone rang while we were eating.", "He found a small shell on the beach.",
        "The little dragon could not fly yet."],
    4: ["Yesterday we visited our grandparents in the country.", "The weather was cold, so I wore a thick scarf.",
        "My friend and I built a castle with old boxes.", "The library is quiet because people are reading.",
        "We should always wash our hands before dinner.", "The squirrel climbed quickly up the tall tree.",
        "My sister thought the puzzle was really difficult."],
    5: ["Although the journey was long, everybody enjoyed the beautiful view.",
        "The girl next door plays the piano every afternoon.",
        "Scientists believe that dolphins talk to each other with special sounds.",
        "Because of the thunderstorm, the football match was cancelled.",
        "Our class wrote a surprising story about a friendly dragon.",
        "The brave knight carefully crossed the narrow bridge at night."],
}
MODES = {"look": "👀 Look, hide, write", "copy": "📝 Copy (the sentence stays)", "listen": "🎧 Listen & write"}


def pick_writing(level, used=(), rng=random):
    """Never-written sentences first; when all are done, the one written the longest time ago."""
    options = [(level * 100 + i, t) for i, t in enumerate(WRITING_TEXTS[level])]
    used = list(used)
    fresh = [o for o in options if o[0] not in set(used)]
    if fresh:
        return rng.choice(fresh)
    last = {tid: k for k, tid in enumerate(used)}
    return min(options, key=lambda o: last.get(o[0], -1))


def writing_level(df_w, cap=5):
    """From the last 3 FIRST tries: >= 90% of words right -> harder, <= 50% -> easier."""
    if df_w is None or len(df_w) == 0:
        return 1
    first = df_w[df_w.attempt == 1].tail(3)
    if first.empty:
        return 1
    lvl = int(first.level.iloc[-1])
    acc = float(first.word_acc.mean())
    if len(first) >= 2 and acc >= 0.9:
        lvl += 1
    elif acc <= 0.5:
        lvl -= 1
    return max(1, min(cap, lvl))


# ------------------------------------------------------------------ checking what was written
MIRROR = {("b", "d"), ("d", "b"), ("p", "q"), ("q", "p"), ("m", "w"), ("w", "m"), ("n", "u"), ("u", "n")}
VOWELS = set("aeiou")
TIPS = {
    "mirror": "'b' and 'd' (or 'p' and 'q') are mirror letters. Trick: make a 'bed' with your two thumbs up 👍👍: "
              "b on the left, d on the right.",
    "swap": "Two letters swapped places. Say the word slowly and write the sounds in order.",
    "missing": "A letter is missing. Tap each sound with a finger while you write.",
    "extra": "There is an extra letter. Read your word back slowly, one letter at a time.",
    "double": "Watch the double letters (like 'll', 'ss', 'tt').",
    "vowel": "The middle sound (a, e, i, o, u) changed. Listen to it carefully.",
    "spelling": "This word has a tricky spelling. Look, say, cover, write, check!",
    "missing_word": "A word is missing. Point at each word when you check your sentence.",
}


def _tok(s):
    return re.findall(r"[A-Za-z0-9']+", s or "")


def _undouble(w):
    return re.sub(r"(.)\1", r"\1", w)


def slip_type(target, got):
    """Kind of spelling slip between the right word and the written word (lower case)."""
    t, g = target.lower(), got.lower()
    if len(t) == len(g):
        diff = [k for k in range(len(t)) if t[k] != g[k]]
        if len(diff) == 1 and (t[diff[0]], g[diff[0]]) in MIRROR:
            return "mirror"
        if len(diff) == 2 and diff[1] == diff[0] + 1 and t[diff[0]] == g[diff[1]] and t[diff[1]] == g[diff[0]]:
            return "swap"
        if len(diff) == 1 and t[diff[0]] in VOWELS and g[diff[0]] in VOWELS:
            return "vowel"
    if t != g and _undouble(t) == _undouble(g):
        return "double"
    if len(g) == len(t) - 1 and difflib.SequenceMatcher(a=t, b=g).ratio() >= 0.75:
        return "missing"
    if len(g) == len(t) + 1 and difflib.SequenceMatcher(a=t, b=g).ratio() >= 0.75:
        return "extra"
    return "spelling"


def letter_marks(target, got):
    """For each letter of the right word: True if the child wrote it in the right place, False otherwise."""
    sm = difflib.SequenceMatcher(a=target.lower(), b=got.lower(), autojunk=False)
    ok = [False] * len(target)
    for tag, i1, i2, _, _ in sm.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                ok[k] = True
    edits = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    return [(c, o) for c, o in zip(target, ok)], edits


def compare_writing(target, written):
    """Word-by-word and letter-by-letter check of a written sentence (case ignored for spelling)."""
    T, W = _tok(target), _tok(written)
    tl, wl = [w.lower() for w in T], [w.lower() for w in W]
    words, extra = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=tl, b=wl, autojunk=False).get_opcodes():
        if tag == "equal":
            words += [dict(word=w, got=w, status="ok", letters=[(c, True) for c in w], edits=0, slip=None)
                      for w in T[i1:i2]]
            continue
        tw, ww = T[i1:i2], W[j1:j2]
        k = 0
        for k, w in enumerate(tw):
            g = ww[k] if k < len(ww) else ""
            if g and difflib.SequenceMatcher(a=w.lower(), b=g.lower()).ratio() >= 0.4:
                letters, edits = letter_marks(w, g)
                words.append(dict(word=w, got=g, status="spelling", letters=letters, edits=edits,
                                  slip=slip_type(w, g)))
            else:
                words.append(dict(word=w, got="", status="missing", letters=[(c, False) for c in w],
                                  edits=len(w), slip="missing_word"))
                if g:
                    extra.append(g)
        extra += ww[len(tw):]
    n = len(T)
    n_ok = sum(w["status"] == "ok" for w in words)
    letters_ok = difflib.SequenceMatcher(a="".join(tl), b="".join(wl), autojunk=False).ratio() if tl else 0.0
    s = (written or "").strip()
    slips = [w["slip"] for w in words if w["slip"]]
    return dict(word_acc=n_ok / n if n else 0.0, letter_acc=letters_ok, n_words=n,
                n_wrong=n - n_ok, words=words, extra=extra,
                capital_ok=(not T) or (s[:1].isupper() if target.strip()[:1].isupper() else True),
                end_ok=(not s) or (s[-1:] in ".!?") if target.strip()[-1:] in ".!?" else True,
                tips=[TIPS[k] for k in dict.fromkeys(slips)][:3],
                errors=[(w["word"].lower(), w["got"].lower()) for w in words if w["status"] != "ok"])


def writing_feedback(res):
    if res["n_words"] and res["n_wrong"] == 0 and not res["extra"]:
        msg = "Every word is spelled correctly! 🌟"
    else:
        msg = (f"You wrote {res['n_words'] - res['n_wrong']} of {res['n_words']} words correctly "
               f"({res['letter_acc'] * 100:.0f}% of the letters).")
        if res["extra"]:
            msg += " Extra word(s): " + ", ".join(f"'{e}'" for e in res["extra"][:3]) + "."
    notes = []
    if not res["capital_ok"]:
        notes.append("start with a capital letter")
    if not res["end_ok"]:
        notes.append("end with a full stop")
    if notes:
        msg += " Small reminder (no points lost): " + " and ".join(notes) + "."
    return msg


def tricky_words(df_w, top=10):
    """Words the child misspelled most often (from the 'errors' column, JSON list of [word, written])."""
    import json
    if df_w is None or len(df_w) == 0:
        return []
    c = Counter()
    for e in df_w.errors.dropna():
        for w, _ in json.loads(e):
            if len(w) >= 2:
                c[w] += 1
    return [w for w, _ in c.most_common(top)]


# ------------------------------------------------------------------ word games
COMMON = """a about after again all also am an and any are as ask at away baby back bad bag be bean beat been
before best big bin bird bit black blue boat body bone both box boy brother but buy by call came can car care
cat cold come cook cool cop cot could cub cut dad day did die dig dim din dip do does dog done dot down draw
drew drop dry dub each ear eat egg end even ever eye face far fast fat feed feel feet fell few fin find fine fit
five fly for four free friend frog from fun game gas get girl give go god going gone good got green grow had hand
hard has hat have he head hear help her here hid high him his hit hold home hop hot how hug hum i if in into is
it its jet job jog jug just keep kid kind kit knew know lab lap last late left leg let lid like line lip lit
live log long look lot love low mad made man many map mat may me men met mix mob mom mop more most much mug mum
must my nap near need net new nib nip nod not now nut of off old on one only open or our out over own pad pal pan
park pat pay peg pen pet pick pie pig pin pit play pod pot pub pull pun pup put ran rat read red rib rid rig rim
rip rob rod rot rub rug run sad said sat saw say sea see set she shed ship shop shot show sip sit six so some son
soon sop sub sum sun tab tag tan tap tea tell ten than that the them then they thin this tin tip to toe ton too
top toy try tub tug two up us van vet wag was way we web wed well went wet what when who why wig will win wit
with won word work would yes yet you zip act fiend fried dug cut bud dud tug beg rag fog
bat ate eat tea sea ant tan nab ban den end ned bin nib pot opt"""


SPELL_WORDS = {
    1: ["cat", "dog", "sun", "bed", "red", "big", "bus", "hat", "pig", "cup", "box", "fox", "bag", "leg", "pen",
        "ten", "map", "net", "jam", "duck", "fish", "frog", "ship", "book", "door", "ball", "tree", "milk", "desk",
        "bird", "hand", "drum", "bell"],
    2: ["house", "horse", "apple", "green", "train", "plant", "sleep", "clock", "black", "brown", "table", "water",
        "happy", "mouse", "snake", "beach", "chair", "bread", "dream", "dragon", "garden", "rabbit", "pencil",
        "window", "yellow", "little", "purple", "spider", "bubble", "doctor"],
    3: ["friend", "because", "school", "people", "laugh", "beautiful", "picture", "thought", "different",
        "birthday", "together", "children", "special", "believe", "enough", "answer", "island", "knife",
        "night", "light", "would", "could", "said", "does", "where", "basket", "kitchen", "bridge", "question"],
}
REAL = {w for ws in SPELL_WORDS.values() for w in ws} | {
    "bad", "dad", "bog", "god", "dig", "big", "bat", "tab", "pot", "top", "pat", "tap", "now", "own", "won", "was",
    "saw", "on", "no", "bet", "but", "bit", "bot", "hot", "hit", "hut", "pet", "pit", "put", "ran", "run", "sit",
    "set", "ten", "tin", "ton", "pan", "pin", "pun", "fan", "fin", "fun", "led", "lid", "lad", "rod", "rid",
    "nap", "pan", "mad", "made", "mud", "bud", "bid", "hate", "hat", "there", "their", "were", "wear", "here",
    "hear", "whole", "hole", "knight", "night", "write", "right", "would", "wood", "quite", "quiet", "form", "from",
    "horse", "hoarse", "house", "dear", "deer", "bear", "bare", "pear", "pair", "sale", "sail", "tail", "tale",
    "bead", "bean", "dean", "bard", "lamp", "plum", "plan", "palm", "dog", "god", "bog", "bed",
    "deb", "bud", "dub", "pod", "bop", "dip", "bib", "did", "pip", "pop", "pup", "dub", "duck", "buck", "puck",
    "clock", "block", "black", "back", "bake", "lake", "take", "made", "maid", "pull", "bull", "dull", "doll",
    "bell", "dell", "drum", "dram", "brown", "drown", "crown", "frown", "dream", "bream", "cream", "beach", "peach",
    "reach", "teach", "bread", "dread", "tread", "pencil", "spider", "doctor", "quilt", "quit", "though", "through",
    "tough", "dose", "does", "doe", "rabbit", "rabid", "brag", "grab", "dab"} | set(COMMON.split())

SWAP_VOWEL = {"a": "e", "e": "i", "i": "e", "o": "u", "u": "o"}
PHONETIC = [("ph", "f"), ("ck", "k"), ("igh", "ite"), ("ee", "ea"), ("ea", "ee"), ("ou", "ow"), ("c", "k"),
            ("k", "c"), ("ai", "ay"), ("tion", "shun"), ("se", "ce"), ("le", "el"), ("er", "ur"), ("kn", "n"),
            ("wh", "w"), ("gh", "f"), ("ie", "ei"), ("ei", "ie"), ("au", "ar"), ("dge", "ge"), ("ch", "tch")]


def misspellings(word, rng=random):
    """Plausible wrong spellings: mirror letters, swapped letters, a letter dropped or doubled,
    a changed vowel, a sound written another way. Real words are removed."""
    w, out = word.lower(), set()
    for k, ch in enumerate(w):
        for a, b in MIRROR:
            if ch == a:
                out.add(w[:k] + b + w[k + 1:])
        if ch in SWAP_VOWEL:
            out.add(w[:k] + SWAP_VOWEL[ch] + w[k + 1:])
        if k < len(w) - 1 and w[k] != w[k + 1]:
            out.add(w[:k] + w[k + 1] + w[k] + w[k + 2:])
        if len(w) >= 4 and 0 < k:
            out.add(w[:k] + w[k + 1:])
    out.add(_undouble(w) if _undouble(w) != w else w + w[-1] if w[-1] not in VOWELS else w)
    for a, b in PHONETIC:
        if a in w:
            out.add(w.replace(a, b, 1))
    out = sorted(o for o in out if o != w and o not in REAL and len(o) >= 2 and o.isalpha())
    rng.shuffle(out)
    return out


def _spelling(level, rng, ctx):
    tricky = [w for w in (ctx.get("tricky") or []) if w.isalpha() and 2 <= len(w) <= 12]
    from_tricky = bool(tricky) and rng.random() < 0.5
    word = rng.choice(tricky) if from_tricky else rng.choice(SPELL_WORDS[level])
    wrong = misspellings(word, rng)
    if len(wrong) < 2:
        return None
    k = 2 if level == 1 else 3
    choices = [word] + wrong[:k]
    return item(gen_id("spell", word, *sorted(choices)), "Spelling", level,
                "🔊 Listen to the word. Which one is written correctly?", choices, word,
                f"'{word}' is written {'-'.join(word)}.", say=word, tag="⭐ one of your tricky words" if from_tricky else None,
                hint="Say the word slowly and listen to each sound.")


SYLLABLES = {
    1: ["cat", "dog", "sun", "fish", "frog", "tree", "bread", "ship", "school", "night", "cake", "house", "chair",
        "rab-bit", "pen-cil", "win-dow", "ap-ple", "gar-den", "mon-key", "ta-ble", "ti-ger", "ro-bot", "piz-za"],
    2: ["rain-bow", "sun-shine", "teach-er", "doc-tor", "kit-ten", "ba-na-na", "el-e-phant", "but-ter-fly",
        "di-no-saur", "to-ma-to", "com-pu-ter", "um-brel-la", "kan-ga-roo", "oc-to-pus", "po-ta-to", "lem-on",
        "spi-der", "drag-on", "bus"],
    3: ["hol-i-day", "croc-o-dile", "wa-ter-mel-on", "cat-er-pil-lar", "hel-i-cop-ter", "al-li-ga-tor",
        "cal-cu-la-tor", "mac-a-ro-ni", "av-o-ca-do", "tel-e-vi-sion", "dan-de-li-on", "di-no-saur", "but-ter-fly",
        "pen-guin", "gi-raffe", "straw-ber-ry"],
}


PICS = {"cat": "🐱", "dog": "🐶", "sun": "☀️", "fish": "🐟", "frog": "🐸", "tree": "🌳", "bread": "🍞", "ship": "🚢",
        "school": "🏫", "night": "🌙", "cake": "🎂", "house": "🏠", "chair": "🪑", "rabbit": "🐰", "pencil": "✏️",
        "window": "🪟", "apple": "🍎", "garden": "🌷", "monkey": "🐒", "table": "🍽️", "tiger": "🐯", "robot": "🤖",
        "pizza": "🍕", "banana": "🍌", "elephant": "🐘", "butterfly": "🦋", "dinosaur": "🦕", "tomato": "🍅",
        "umbrella": "☂️", "kangaroo": "🦘", "octopus": "🐙", "potato": "🥔", "rainbow": "🌈", "teacher": "🧑‍🏫",
        "doctor": "🧑‍⚕️", "kitten": "🐱", "computer": "💻", "lemon": "🍋", "spider": "🕷️", "dragon": "🐉", "bus": "🚌",
        "crocodile": "🐊", "watermelon": "🍉", "caterpillar": "🐛", "helicopter": "🚁", "penguin": "🐧",
        "giraffe": "🦒", "strawberry": "🍓", "avocado": "🥑", "television": "📺", "holiday": "🏖️"}


def _train(parts):
    wagons = "".join(f"<span style='display:inline-block;margin:0 .15rem;padding:.25rem .6rem;border-radius:8px;"
                     f"background:#ffcc80;border:2px solid #e65100'>{p}</span>" for p in parts)
    return f"🚂 {wagons}"


def _syllables(level, rng, ctx):
    """Syllable train (dyslexia document): each wagon is one syllable. A sound model comes first in the hint."""
    split = rng.choice(SYLLABLES[level])
    word, n = split.replace("-", ""), split.count("-") + 1
    choices = [1, 2, 3] if level == 1 else [1, 2, 3, 4] if level == 2 else [2, 3, 4, 5]
    if n not in choices:
        choices = sorted(set(choices[1:] + [n]))
    pic = PICS.get(word, "") if level < 3 else ""  # level 1-2: a picture helps; level 3: less familiar words
    return item(gen_id("syl", word), "Syllable train", level,
                f"🚂 Help the train! How many **wagons** (syllables) does **{word}** need?", choices, n,
                f"{word} = {' · '.join(split.split('-'))}: {n} wagon{'s' if n > 1 else ''}. "
                "You separated the parts of the word!", say=word, keep_order=True,
                html=f"<div style='font-size:2.6rem;text-align:center;letter-spacing:.08em'>{pic} {word}</div>",
                praise="You separated the parts of the word well! 🚂",
                hint="Listen to the model first: ba · na · na = 3 wagons 🚂🚃🚃🚃. Now clap your word: "
                     "one clap = one wagon.")


RHYMES = [["cat", "hat", "bat", "mat", "rat"], ["dog", "log", "frog", "fog", "jog"], ["sun", "run", "fun", "bun"],
          ["cake", "lake", "make", "snake", "bake"], ["bee", "tree", "see", "three", "knee"],
          ["king", "ring", "sing", "wing", "swing"], ["car", "star", "jar", "far"], ["boat", "coat", "goat", "note"],
          ["night", "light", "kite", "bright", "white"], ["bed", "red", "head", "bread", "said"],
          ["chair", "bear", "hair", "pear"], ["moon", "spoon", "soon", "balloon"], ["ball", "wall", "tall", "small"],
          ["fish", "dish", "wish"], ["book", "look", "cook", "hook"]]


def _rhymes(level, rng, ctx):
    """Rhyme maze (dyslexia document): level 1 = 2 words, level 2 = 3-4 words, level 3 = tick ALL the rhymes."""
    g = rng.choice([r for r in RHYMES if len(r) >= 4] if level == 3 else RHYMES)
    others = [w for grp in RHYMES if grp is not g for w in grp]
    praise = "Those words rhyme because their endings sound alike! 🌀"
    if level < 3:
        target, ans = rng.sample(g, 2)
        dist = rng.sample(others, 1 if level == 1 else 3)
        return item(gen_id("rhyme", target, ans, *sorted(dist)), "Rhyme maze", level,
                    f"🌀 Rhyme maze: to open the door 🚪, choose a word that rhymes with **{target}**.",
                    [ans] + dist, ans, f"'{target}' and '{ans}' rhyme because their endings sound alike.",
                    say=f"{target}. " + ". ".join([ans] + dist), praise=praise,
                    hint="Say the words aloud and listen to the END of each word.")
    target, *rest = rng.sample(g, min(len(g), 4))
    dist = rng.sample(others, 3)
    return item(gen_id("rhyme3", target, *sorted(rest), *sorted(dist)), "Rhyme maze", level,
                f"🌀 Rhyme maze: tick **all** the words that rhyme with **{target}** to get out!",
                rest + dist, " + ".join(rest), f"These words rhyme with '{target}': {', '.join(rest)}. "
                "Some rhymes are spelled differently, but they sound alike at the end.",
                say=f"{target}. " + ". ".join(rest + dist), multi=True, answers=rest, praise=praise,
                hint="Say the target word, then each word: does the end sound the same?")


STARTERS = {"is", "can", "are", "am", "do", "does", "will", "did", "has", "have", "was", "were", "could", "should"}


def _order(level, rng, ctx):
    tid, sent = rng.choice([(lv * 100 + i, s) for lv in (level, min(level + 1, 3))
                            for i, s in enumerate(WRITING_TEXTS[lv])])
    words = [w if w == "I" else w.lower() for w in _tok(sent)]
    right = " ".join(words)
    wrong = set()
    for _ in range(40):
        w = words[:]
        i = rng.randrange(len(w) - 1)
        j = i + 1 if rng.random() < 0.7 else rng.randrange(len(w))
        w[i], w[j] = w[j], w[i]
        if w != words and w[0] not in STARTERS:
            wrong.add(" ".join(w))
        if len(wrong) >= 2:
            break
    if len(wrong) < 2:
        return None
    mixed = words[:]
    while mixed == words:
        rng.shuffle(mixed)
    chips = " ".join(f"<span style='display:inline-block;margin:.25rem;padding:.25rem .7rem;border-radius:10px;"
                     f"background:rgba(108,92,231,.14)'>{w}</span>" for w in mixed)
    return item(gen_id("order", tid, *sorted(wrong)), "Word order", level,
                "These words are mixed up. Which sentence is in the right order?", [right] + sorted(wrong), right,
                f"The right order is: '{sent}'", html=f"<div style='font-size:1.5rem;text-align:center'>{chips}</div>",
                say=None, hint="Find the word that starts the sentence first (who or what?).")


import games_content as _g  # noqa: E402

# v6: "Copy the rhythm" (hearing and keeping sound sequences, a building block of reading) and
# "Treasure map" (left / right and following directions in order)
import dyslexia_content as _dy  # noqa: E402

# final version: the 12 games of the dyslexia document. Question games are here; Build the word, Sentence puzzle,
# Magic echo and My story (level 3) are interactive (tab "🧱 Build & read" in app.py).
GAME_CATEGORIES = ["Spelling", "Syllable train", "Rhyme maze", "Word order", "Copy the rhythm", "Treasure map",
                   "Sound detective", "Twin words", "Hidden letters", "Word market", "Meaning hunt",
                   "Prefixes & suffixes", "Story in pictures"]
WORD_BANK = Bank(GAME_CATEGORIES, (), {"Spelling": _spelling, "Syllable train": _syllables, "Rhyme maze": _rhymes,
                                       "Word order": _order, "Copy the rhythm": _g.rhythm,
                                       "Treasure map": _g.treasure, "Sound detective": _dy.sound_detective,
                                       "Twin words": _dy.twin_words, "Hidden letters": _dy.hidden_letters,
                                       "Word market": _dy.word_market, "Meaning hunt": _dy.meaning_hunt,
                                       "Prefixes & suffixes": _dy.affixes, "Story in pictures": _dy.story_pictures})


def pick_game(df_act, cap=3, category=None, rng=random, recent=(), tricky=()):
    return WORD_BANK.pick(df_act, cap, category, rng, recent, ctx={"tricky": list(tricky)})


def writing_script(name, text, res):
    """What the voice says after a written sentence with mistakes: the sentence slowly, then each tricky word
    spelled letter by letter."""
    wrong = [w["word"] for w in res["words"] if w["status"] != "ok"][:3]
    intro = f"Good try{', ' + name if name else ''}. Here is the sentence. "
    spell = " ".join(f"{w}: {', '.join(w)}." for w in wrong)
    return intro + text + (" Let's spell the tricky words. " + spell if spell else "")


def marks_html(res):
    """Coloured correction: green = right, orange = spelling to fix (wrong letters in red), [red] = missing."""
    parts = []
    for w in res["words"]:
        if w["status"] == "ok":
            parts.append(f"<span style='color:#2e7d32'>{w['word']}</span>")
        elif w["status"] == "spelling":
            fixed = "".join(c if ok else f"<u style='color:#c62828;font-weight:700'>{c}</u>" for c, ok in w["letters"])
            parts.append(f"<span style='color:#ef6c00'><s>{w['got']}</s> → <b>{fixed}</b></span>")
        else:
            parts.append(f"<span style='color:#c62828'>[<b>{w['word']}</b>]</span>")
    parts += [f"<span style='color:#9e9e9e'><s>+{e}</s></span>" for e in res["extra"]]
    return ("<div style='font-size:1.4rem;line-height:2.2;letter-spacing:.04em'>" + " ".join(parts) + "</div>"
            "<div style='font-size:.85rem;opacity:.75'>green = correct · orange = spelling to fix "
            "(the red letters) · [red] = missing word · grey = extra word</div>")
