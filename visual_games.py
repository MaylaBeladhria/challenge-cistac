"""v7 visual games (no reading needed): picture PUZZLE and HIDDEN LEAVES.

| Game          | Skills (practice only)                                   | Profiles                 |
|---------------|----------------------------------------------------------|--------------------------|
| 🧩 Puzzle      | visual-spatial thinking, planning, persistence           | autism, ADHD, dyslexia   |
| 🍂 Leaves      | visual discrimination (look-alike shapes), visual memory | autism, ADHD, dyslexia   |

Why these profiles: both games are calm, without timer or reading, with clear rules and a visible goal (autism);
short, rewarding and they train sustained attention and working memory (ADHD); they train telling look-alike
shapes apart and visual memory, with a success that does not depend on reading (dyslexia).

Levels (adapted from the child's last 3 games of this kind: success x3 -> harder, failure x2 -> easier)
  Puzzle  1: 4 pieces, the faded picture is shown in each empty place
          2: 9 pieces, a small model of the picture is shown
          3: 12 pieces, no model (a "peek" button shows it if needed)
  Leaves  1: 8 leaves face up, find the TWO that are exactly the same
          2: memory game, 8 hidden cards (4 pairs); you may look at them first, then they are hidden
          3: memory game, 12 hidden cards (6 pairs) with look-alike leaves (same shape or same colour)
The pictures are drawn by the code (Pillow / SVG), so every game is new.
"""
import io
import math
import random

from PIL import Image, ImageDraw

from practice import gen_id

# =================================================================== PUZZLE
W, H = 480, 360
GRIDS = {1: (2, 2), 2: (3, 3), 3: (3, 4)}  # rows, cols


def _rand_color(rng, base, spread=30):
    return tuple(max(0, min(255, c + rng.randint(-spread, spread))) for c in base)


def _cloud(d, x, y, s=1.0):
    for dx, dy, r in ((0, 0, 16), (18, -8, 20), (38, 0, 16), (18, 6, 16)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill="white")


def _flower(d, x, y, col):
    for a in range(0, 360, 72):
        px, py = x + 9 * math.cos(math.radians(a)), y + 9 * math.sin(math.radians(a))
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=col)
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(250, 210, 40))


def _star(d, x, y, r, col):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = math.radians(-90 + 36 * k)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=col)


def _decorate(d, rng, rows, cols, scene, horizon):
    """One small object in every piece, so that no two pieces look exactly the same."""
    th, tw = H / rows, W / cols
    for r in range(rows):
        for c in range(cols):
            x = c * tw + rng.uniform(0.2, 0.75) * tw
            y = r * th + rng.uniform(0.25, 0.75) * th
            if scene == "space":
                _star(d, x, y, rng.randint(5, 9), (255, 255, rng.randint(150, 230)))
            elif y < horizon - 10:
                if scene == "sea" and rng.random() < 0.5:
                    d.line([x - 10, y, x - 3, y - 6, x, y, x + 3, y - 6, x + 10, y], fill=(60, 60, 60), width=2)
                else:
                    _cloud(d, x - 18, y, 0.6)
            elif scene == "sea":
                d.arc([x - 14, y - 6, x + 14, y + 6], 200, 340, fill=(255, 255, 255), width=3)
            else:
                _flower(d, x, y, rng.choice([(230, 60, 90), (150, 80, 220), (255, 140, 0), (240, 240, 240)]))


def make_picture(rng, rows, cols):
    scene = rng.choice(["house", "sea", "space", "garden"])
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    horizon = rng.randint(200, 240)
    if scene == "space":
        d.rectangle([0, 0, W, H], fill=_rand_color(rng, (20, 24, 70), 15))
        px, py, pr = rng.randint(90, 160), rng.randint(90, 150), rng.randint(40, 55)
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=_rand_color(rng, (230, 150, 60)))
        d.arc([px - pr - 30, py - 18, px + pr + 30, py + 18], 160, 380, fill=(250, 220, 160), width=6)
        rx, ry = rng.randint(300, 380), rng.randint(120, 200)
        d.rectangle([rx - 18, ry - 50, rx + 18, ry + 50], fill=(235, 235, 245))
        d.polygon([(rx - 18, ry - 50), (rx + 18, ry - 50), (rx, ry - 90)], fill=(220, 50, 60))
        d.ellipse([rx - 9, ry - 25, rx + 9, ry - 7], fill=(80, 170, 230))
        d.polygon([(rx - 12, ry + 50), (rx + 12, ry + 50), (rx, ry + 90)], fill=(255, 160, 30))
        d.ellipse([380, 260, 450, 330], fill=(220, 220, 230))
    else:
        sky = _rand_color(rng, (135, 200, 250), 20)
        d.rectangle([0, 0, W, horizon], fill=sky)
        sx, sy = rng.choice([(70, 60), (410, 60), (240, 50)])
        d.ellipse([sx - 32, sy - 32, sx + 32, sy + 32], fill=(255, 210, 40))
        if scene == "sea":
            d.rectangle([0, horizon, W, H], fill=_rand_color(rng, (40, 120, 200), 20))
            bx = rng.randint(110, 330)
            d.polygon([(bx - 70, horizon - 5), (bx + 70, horizon - 5), (bx + 45, horizon + 30), (bx - 45, horizon + 30)],
                      fill=_rand_color(rng, (170, 70, 40)))
            d.line([bx, horizon - 5, bx, horizon - 110], fill=(90, 60, 30), width=5)
            d.polygon([(bx + 3, horizon - 105), (bx + 3, horizon - 15), (bx + 70, horizon - 15)], fill=(250, 250, 250))
            fx = rng.randint(40, 420)
            d.ellipse([fx - 20, 300, fx + 20, 322], fill=(255, 140, 0))
            d.polygon([(fx + 18, 311), (fx + 34, 298), (fx + 34, 324)], fill=(255, 140, 0))
        else:
            d.rectangle([0, horizon, W, H], fill=_rand_color(rng, (90, 180, 70), 20))
            if scene == "house":
                hx = rng.randint(150, 300)
                body = _rand_color(rng, (230, 120, 90), 40)
                d.rectangle([hx - 70, horizon - 90, hx + 70, horizon + 20], fill=body)
                d.polygon([(hx - 85, horizon - 90), (hx + 85, horizon - 90), (hx, horizon - 160)],
                          fill=_rand_color(rng, (150, 40, 40), 30))
                d.rectangle([hx - 15, horizon - 30, hx + 15, horizon + 20], fill=(110, 70, 40))
                for wx in (hx - 50, hx + 25):
                    d.rectangle([wx, horizon - 70, wx + 25, horizon - 45], fill=(200, 235, 255))
                tx = 60 if hx > 240 else 410
            else:
                tx = rng.randint(60, 140)
                for k in range(3):
                    fx = 220 + 80 * k
                    d.line([fx, horizon + 70, fx, horizon - 10], fill=(40, 130, 40), width=5)
                    _flower(d, fx, horizon - 15, rng.choice([(230, 60, 90), (150, 80, 220), (255, 140, 0)]))
                d.ellipse([340, 60, 380, 90], fill=(255, 200, 60))  # butterfly
                d.ellipse([370, 60, 410, 90], fill=(255, 200, 60))
            d.rectangle([tx - 10, horizon - 50, tx + 10, horizon + 20], fill=(110, 70, 40))
            d.ellipse([tx - 45, horizon - 120, tx + 45, horizon - 30], fill=_rand_color(rng, (40, 140, 50), 20))
    _decorate(d, rng, rows, cols, scene, horizon)
    return img, scene


def _png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def _tile_frame(tile):
    d = ImageDraw.Draw(tile)
    d.rectangle([0, 0, tile.width - 1, tile.height - 1], outline=(90, 90, 90), width=2)
    return tile


def new_puzzle(level, rng=random):
    rows, cols = GRIDS[level]
    img, scene = make_picture(rng, rows, cols)
    tw, th = W // cols, H // rows
    tiles, ghosts = [], []
    for r in range(rows):
        for c in range(cols):
            t = img.crop((c * tw, r * th, (c + 1) * tw, (r + 1) * th))
            tiles.append(_png(_tile_frame(t.copy())))
            g = Image.blend(t, Image.new("RGB", t.size, "white"), 0.75) if level == 1 else \
                Image.new("RGB", t.size, (238, 238, 238))
            ghosts.append(_png(_tile_frame(g)))
    order = list(range(rows * cols))
    while order == sorted(order):
        rng.shuffle(order)
    return dict(kind="puzzle", level=level, rows=rows, cols=cols, scene=scene, tiles=tiles, ghosts=ghosts,
                model=_png(img.resize((W // 2, H // 2))), tray=order, placed={}, selected=None,
                mistakes=0, peeks=0, done=False, logged=False, id=gen_id("puzzle", level, scene, *order),
                msg=None)


def puzzle_take(pz, piece):
    if piece in pz["tray"]:
        pz["selected"] = piece
        pz["msg"] = None


def puzzle_put(pz, slot):
    """Put the selected piece in a place. Only the right place accepts it (no wrong picture is ever built)."""
    p = pz["selected"]
    if p is None or slot in pz["placed"]:
        return None
    if p == slot or pz["tiles"][p] == pz["tiles"][slot]:
        pz["placed"][slot] = p
        pz["tray"].remove(p)
        pz["selected"] = None
        pz["msg"] = (True, "It fits! 🧩")
        if not pz["tray"]:
            pz["done"] = True
            pz["msg"] = (True, "Bravo! You finished the puzzle. 🌟")
        return True
    pz["mistakes"] += 1
    pz["msg"] = (False, "This piece goes somewhere else. Look at the colours on its edges and try another place.")
    return False


def puzzle_success(pz):
    return pz["mistakes"] <= len(pz["tiles"]) // 2


# =================================================================== LEAVES
LEAF_COLORS = {"green": ("#6cbf3a", "#3d7a1c"), "dark green": ("#2e8b3a", "#1b5422"),
               "yellow": ("#f6c21c", "#b7860b"), "orange": ("#f08a1c", "#a3540a"),
               "red": ("#e23b2a", "#931d12"), "brown": ("#b0703a", "#6d421d")}


def _serrated():
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        r = 1.0 if k % 2 == 0 else 0.9
        x = 50 + 30 * r * math.sin(a)
        y = 55 - 45 * r * math.cos(a)
        pts.append(f"{x:.1f},{y:.1f}")
    return f"<polygon points='{' '.join(pts)}' fill='{{f}}' stroke='{{s}}' stroke-width='2'/>"


LEAF_SHAPES = {
    "oval": "<path d='M50 8 C82 32 84 72 50 102 C16 72 18 32 50 8 Z' fill='{f}' stroke='{s}' stroke-width='2'/>",
    "heart": "<path d='M50 10 C56 32 92 40 88 70 C86 95 60 102 50 90 C40 102 14 95 12 70 C8 40 44 32 50 10 Z' "
             "fill='{f}' stroke='{s}' stroke-width='2'/>",
    "maple": "<polygon points='50,4 58,28 76,17 70,40 93,34 81,55 96,62 70,72 73,90 55,79 52,100 48,100 45,79 "
             "27,90 30,72 4,62 19,55 7,34 30,40 24,17 42,28' fill='{f}' stroke='{s}' stroke-width='2'/>",
    "oak": "<path d='M50 6 Q63 10 59 22 Q74 20 69 34 Q84 36 73 48 Q88 55 73 64 Q84 75 67 78 Q71 93 56 90 L52 100 "
           "L48 100 L44 90 Q29 93 33 78 Q16 75 27 64 Q12 55 27 48 Q16 36 31 34 Q26 20 41 22 Q37 10 50 6 Z' "
           "fill='{f}' stroke='{s}' stroke-width='2'/>",
    "chestnut": "".join(f"<ellipse cx='50' cy='64' rx='9' ry='30' transform='rotate({a} 50 96)' fill='{{f}}' "
                        f"stroke='{{s}}' stroke-width='2'/>" for a in (-60, -30, 0, 30, 60)),
    "serrated": _serrated(),
    "willow": "<path d='M50 4 C63 40 63 80 50 104 C37 80 37 40 50 4 Z' fill='{f}' stroke='{s}' stroke-width='2'/>",
}


def leaf_svg(shape, color, size=96):
    f, s = LEAF_COLORS[color]
    k = 0.45 if shape == "willow" else 1.0  # thin leaf: shorter side veins
    veins = ("" if shape == "chestnut" else
             f"<line x1='50' y1='14' x2='50' y2='100' stroke='{s}' stroke-width='2'/>"
             + "".join(f"<line x1='50' y1='{y}' x2='{50 + dx}' y2='{y - 12}' stroke='{s}' stroke-width='1.4'/>"
                       f"<line x1='50' y1='{y}' x2='{50 - dx}' y2='{y - 12}' stroke='{s}' stroke-width='1.4'/>"
                       for y, dx in ((45, round(14 * k)), (62, round(18 * k)), (79, round(14 * k)))))
    stem = f"<line x1='50' y1='96' x2='50' y2='116' stroke='{s}' stroke-width='3' stroke-linecap='round'/>"
    return (f"<svg width='{size}' height='{size * 1.2:.0f}' viewBox='0 0 100 120' role='img' "
            f"aria-label='{color} {shape} leaf'>{LEAF_SHAPES[shape].format(f=f, s=s)}{veins}{stem}</svg>")


def card_html(number, face, state):
    """state: 'down' (hidden), 'up', 'match' (found pair), 'pick' (selected in the find-two game)."""
    border = {"down": "#8bc34a", "up": "#f2c94c", "match": "#2e7d32", "pick": "#1e88e5"}[state]
    bg = "#e8f5d0" if state == "down" else "#fffaf0"
    inner = ("<div style='font-size:3.4rem;font-weight:800;color:#2e6b1e;line-height:118px'>?</div>"
             if state == "down" else leaf_svg(*face))
    tick = "<div style='position:absolute;top:4px;right:8px;font-size:1.2rem'>✅</div>" if state == "match" else ""
    return (f"<div style='position:relative;text-align:center;border:3px solid {border};border-radius:14px;"
            f"background:{bg};height:132px;margin-bottom:.3rem'>"
            f"<div style='position:absolute;top:4px;left:8px;background:#f6c95a;border-radius:50%;width:26px;"
            f"height:26px;line-height:26px;font-weight:700;color:#4a3000'>{number}</div>{tick}{inner}</div>")


def _leaf_set(rng, n_kinds, look_alike):
    shapes, colors = list(LEAF_SHAPES), list(LEAF_COLORS)
    if not look_alike:
        sh, co = rng.sample(shapes, n_kinds), rng.sample(colors, n_kinds)
        return list(zip(sh, co))
    out = set()
    base_shape, base_color = rng.choice(shapes), rng.choice(colors)
    while len(out) < n_kinds:  # most leaves share the shape OR the colour of another one
        if rng.random() < 0.5:
            out.add((base_shape, rng.choice(colors)))
        else:
            out.add((rng.choice(shapes), base_color))
        if rng.random() < 0.3:
            base_shape, base_color = rng.choice(shapes), rng.choice(colors)
    return list(out)


def new_leaves(level, rng=random):
    if level == 1:  # 8 leaves face up: exactly one pair is identical, the others look alike
        kinds = _leaf_set(rng, 7, look_alike=True)
        cards = kinds + [kinds[0]]
        rng.shuffle(cards)
        phase = "find"
    else:
        kinds = _leaf_set(rng, 4 if level == 2 else 6, look_alike=(level == 3))
        cards = kinds * 2
        rng.shuffle(cards)
        phase = "look" if level == 2 else "play"
    return dict(kind="leaves", level=level, cards=cards, phase=phase, up=[], matched=[], tries=0, done=False,
                logged=False, msg=None, id=gen_id("leaves", level, *[f"{s}{c}" for s, c in cards]))


def leaves_flip(m, i):
    """Turn (or pick) card i. Returns 'pair', 'nopair' or None."""
    if m["done"] or i in m["matched"] or i in m["up"]:
        return None
    if len(m["up"]) == 2:  # two different cards were still visible: hide them first
        m["up"] = []
    m["up"].append(i)
    m["msg"] = None
    if len(m["up"]) < 2:
        return None
    a, b = m["up"]
    m["tries"] += 1
    if m["cards"][a] == m["cards"][b]:
        m["matched"] += [a, b]
        m["up"] = []
        if m["phase"] == "find" or len(m["matched"]) == len(m["cards"]):
            m["done"] = True
            m["msg"] = (True, f"Well done! Leaves {a + 1} and {b + 1} are exactly the same. 🍂" if m["phase"] == "find"
                        else f"Bravo! You found all the pairs in {m['tries']} tries. 🍂")
        else:
            m["msg"] = (True, "A pair! ✅ Keep going.")
        return "pair"
    sa, ca = m["cards"][a]
    sb, cb = m["cards"][b]
    why = ("same colour, but not the same shape" if ca == cb and sa != sb else
           "same shape, but not the same colour" if sa == sb else "not the same")
    m["msg"] = (False, f"Leaves {a + 1} and {b + 1}: {why}. Look carefully and try again.")
    if m["phase"] == "find":
        m["up"] = []
    return "nopair"


def leaves_success(m):
    pairs = 1 if m["phase"] == "find" else len(m["cards"]) // 2
    return m["tries"] <= (2 if pairs == 1 else 2 * pairs + 1)
