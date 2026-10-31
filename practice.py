"""Shared engine for practice questions (autism, ADHD and dyslexia activities).

Why it exists: in v4 the practice questions came from one small fixed list, so a child quickly saw the same
questions again. Here every activity is a *bank* made of
  - static items (hand-written, with {A}/{B}/{C} name placeholders filled with a different name each time), and
  - generators (functions that build a NEW question each time: new emojis, new names, new objects, new orders).

No-repeat rule (`Bank.pick`):
  1. never-seen items first (history is stored per child in the database, so this holds across sessions);
  2. topics rotate in "Mix" mode (the topic practised the longest time ago comes first);
  3. only when everything at that level has been seen, the item seen the LONGEST time ago comes back,
     with new names and shuffled answers, so it still looks different.

Every item is a dict: id, cat, level, q, choices, a, why  [+ optional html, say, memo, hint, keep_order, tag,
multi/answers (tick several), accept (other right answers), praise, rhythm/listen_first]. See games_content.py.
"""
import random
import zlib

NAMES = ["Sam", "Mia", "Leo", "Nora", "Ben", "Omar", "Lina", "Ava", "Yusuf", "Zoe", "Adam", "Sara", "Noah",
         "Ines", "Ali", "Lucy", "Kenji", "Amira", "Tom", "Maya", "Rayan", "Emma", "Hugo", "Lea", "Karim", "Jade"]

GEN_BASE = 1_000_000  # generated items get ids above this, static items stay below


def gen_id(*parts):
    """Stable id for a generated question: the same question always gets the same id (used for no-repeat)."""
    return GEN_BASE + zlib.crc32("|".join(map(str, parts)).encode()) % 1_000_000_000


def item(id_, cat, level, q, choices, a, why, **extra):
    d = dict(id=id_, cat=cat, level=level, q=q, choices=list(choices), a=a, why=why)
    d.update(extra)
    return d


def level_from_history(df, cap=3):
    """Next level from the last 3 answers of this activity: all correct -> harder, at most 1 correct -> easier."""
    if df is None or len(df) == 0:
        return 1
    last = df.tail(3)
    lvl = int(last.level.iloc[-1])
    if len(last) >= 3 and last.correct.sum() == 3:
        lvl += 1
    elif len(last) >= 3 and last.correct.sum() <= 1:
        lvl -= 1
    return max(1, min(cap, lvl))


def _fill_names(it, rng):
    names = rng.sample(NAMES, 3)
    rep = {"{A}": names[0], "{B}": names[1], "{C}": names[2]}

    def f(s):
        if not isinstance(s, str):
            return s
        for k, v in rep.items():
            s = s.replace(k, v)
        return s

    for k in ("q", "a", "why", "html", "say", "memo", "hint"):
        if k in it:
            it[k] = f(it[k])
    for k in ("choices", "accept", "answers"):
        if k in it:
            it[k] = [f(c) for c in it[k]]
    return it


class Bank:
    def __init__(self, categories, static=(), generators=None, max_level=3):
        self.categories = list(categories)
        self.static = list(static)
        self.generators = dict(generators or {})  # category -> fn(level, rng, ctx) -> item | None
        self.max_level = max_level

    # ------------------------------------------------------------ helpers
    def _static(self, cat, level):
        return [i for i in self.static if i["cat"] == cat and i["level"] == level]

    def _fresh(self, cat, level, seen, rng, ctx):
        pool = [i for i in self._static(cat, level) if i["id"] not in seen]
        gen = self.generators.get(cat)
        if gen and (not pool or rng.random() < 0.6):
            for _ in range(40):
                it = gen(level, rng, ctx)
                if it is not None and it["id"] not in seen:
                    return it
        return rng.choice(pool) if pool else None

    def _finish(self, it, rng):
        it = _fill_names(dict(it, choices=[str(c) for c in it["choices"]], a=str(it["a"])), rng)
        if not it.get("keep_order"):
            rng.shuffle(it["choices"])
        return it

    # ------------------------------------------------------------ public API
    def generate(self, cat, level, rng=random, ctx=None):
        """One question of this topic and level (static or generated), ready to show. None if no content."""
        it = self._fresh(cat, level, set(), rng, ctx or {})
        return self._finish(it, rng) if it else None

    def pick(self, df_hist, cap=3, category=None, rng=random, recent=(), ctx=None):
        """Next question for this child. df_hist: this activity's history (columns level, correct, item_id,
        category). recent: ids shown in this session but maybe not answered (skipped questions)."""
        ctx = ctx or {}
        cap = max(1, min(cap, self.max_level))
        lvl = level_from_history(df_hist, cap)
        order_seen = (list(df_hist.item_id) if df_hist is not None and len(df_hist) else []) + list(recent)
        seen = set(order_seen)
        if category:
            cats = [category]
        else:  # topic rotation: topics not practised for the longest time come first
            hist_cats = list(df_hist.category) if df_hist is not None and len(df_hist) and "category" in df_hist else []
            last_used = {c: k for k, c in enumerate(hist_cats)}
            cats = sorted(rng.sample(self.categories, len(self.categories)), key=lambda c: last_used.get(c, -1))
        levels = [lvl] + list(range(lvl - 1, 0, -1)) + list(range(lvl + 1, cap + 1))
        for lv in levels:
            for cat in cats:
                it = self._fresh(cat, lv, seen, rng, ctx)
                if it:
                    return self._finish(it, rng)
        # everything has been seen: bring back the static item seen the longest time ago (new names, new order)
        last_seen = {iid: k for k, iid in enumerate(order_seen)}
        pool = [i for lv in levels for c in cats for i in self._static(c, lv)]
        if pool:
            return self._finish(min(pool, key=lambda i: last_seen.get(i["id"], -1)), rng)
        for c in cats:
            gen = self.generators.get(c)
            it = gen(lvl, rng, ctx) if gen else None
            if it:
                return self._finish(it, rng)
        return None
