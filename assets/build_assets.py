#!/usr/bin/env python3
"""ENOCH asset builder — reads engine templates from index.html, exports PNGs.
Does NOT modify index.html. Run: python assets/build_assets.py"""
from __future__ import annotations
import json, re, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
OUT = Path(__file__).resolve().parent
SCALE = 4  # 32px art -> 128px output width

# ---------------------------------------------------------------------------
# Minimal PNG writer (no Pillow required, but we use Pillow if available)
# ---------------------------------------------------------------------------
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def hex_to_rgba(h: str, a: int = 255) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def grab_block(html: str, name: str) -> str:
    m = re.search(rf"const {name}\s*=\s*\{{", html)
    if not m:
        raise ValueError(f"{name} not found")
    i = m.end() - 1
    depth = 0
    while i < len(html):
        c = html[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return html[m.end() - 1 : i + 1]
        i += 1
    raise ValueError(f"unclosed {name}")


def extract_array(text: str, key: str) -> list[str]:
    m = re.search(rf"{key}\s*:\s*\[", text)
    if not m:
        return []
    i = m.end()
    depth = 1
    start = i
    while i < len(text) and depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    inner = text[start : i - 1]
    return re.findall(r'"([^"]*)"', inner)


def parse_facing_block(block: str, facing: str) -> dict:
    m = re.search(rf"{facing}\s*:\s*\{{", block)
    if not m:
        return {}
    i = m.end() - 1
    depth = 0
    while i < len(block):
        c = block[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                sub = block[m.end() - 1 : i + 1]
                break
        i += 1
    else:
        return {}
    out = {}
    for part in ("body", "idle", "walkA", "walkB", "pass"):
        rows = extract_array(sub, part)
        if rows:
            out[part] = rows
    return out


def parse_template_set(html: str, name: str) -> dict:
    block = grab_block(html, name)
    wh = re.search(r"W\s*:\s*(\d+)", block)
    hh = re.search(r"H\s*:\s*(\d+)", block)
    result = {}
    if wh:
        result["W"] = int(wh.group(1))
    if hh:
        result["H"] = int(hh.group(1))
    for facing in ("down", "up", "side"):
        result[facing] = parse_facing_block(block, facing)
    return result


# Engine palettes (mirrored from PALS — read-only reference)
PALS = {
    "enoch": {"k": "#2a1c10", "H": "#5a3d23", "h": "#42301c", "S": "#e0b48a", "s": "#c29467",
              "E": "#241a10", "R": "#c9b28a", "r": "#a8926c", "Q": "#ded0b2", "B": "#7a5a30",
              "G": "#caa53a", "C": "#8a5a30", "W": "#7a4f28", "M": "#7a5a36", "m": "#553c22"},
    "edna": {"k": "#221224", "H": "#2e2018", "h": "#1c1410", "S": "#dfae84", "s": "#c08f66",
             "E": "#241a10", "R": "#8c5a96", "r": "#714a7a", "Q": "#a571b0", "B": "#d9b13b",
             "G": "#d9b13b", "C": "#d9b13b"},
    "elder": {"k": "#28241e", "H": "#cfc8bd", "h": "#a8a298", "S": "#d6a87e", "s": "#b88a60",
              "E": "#241a10", "R": "#9a948a", "r": "#7c766c", "Q": "#b4aea2", "B": "#5c564c",
              "G": "#8a8478", "C": "#5c564c", "staff": "#7a5a36"},
    "uriel": {"k": "#9a8040", "H": "#ffe9a8", "h": "#dcbc68", "S": "#ffe2c0", "s": "#f0c898",
              "E": "#a87614", "R": "#f6f1ff", "r": "#dcd4ec", "Q": "#ffffff", "B": "#e8c55a",
              "G": "#ffd870", "C": "#e8c55a"},
    "azazel": {"k": "#080510", "H": "#15101e", "h": "#0c0814", "S": "#bfa088", "s": "#a08468",
               "E": "#c2241e", "R": "#241a30", "r": "#170f20", "Q": "#3a2c4e", "B": "#caa53a",
               "G": "#e8c55a", "C": "#caa53a"},
}


def parse_js_templates(html: str) -> tuple[dict, dict, dict]:
    return parse_template_set(html, "TPL"), parse_template_set(html, "TPL_HERO"), PALS


def rows_for_frame(tpl_facing: dict, frame: int) -> list[str]:
    legs = (
        tpl_facing["walkA"] if frame == 1
        else tpl_facing["walkB"] if frame == 2
        else tpl_facing.get("pass", tpl_facing["idle"]) if frame == 3
        else tpl_facing["idle"]
    )
    body = tpl_facing["body"]
    combined = list(body) + list(legs)
    return [str(r).ljust(32, ".")[:32] for r in combined]


def render_sprite(rows: list[str], palette: dict, aw: int, ah: int) -> "Image.Image":
    from PIL import Image, ImageDraw
    w, h = aw * SCALE, ah * SCALE
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    grid = [[ch not in (".", "", " ") for ch in row] for row in rows]

    for y, row in enumerate(rows):
        for x, ch in enumerate(row[:aw]):
            if ch in (".", " ", ""):
                continue
            col = palette.get(ch, "#ff00ff")
            r, g, b = hex_to_rgba(col)[:3]
            for dy in range(SCALE):
                for dx in range(SCALE):
                    px[x * SCALE + dx, y * SCALE + dy] = (r, g, b, 255)

    # rim light (top-left key light) — matches engine pass
    highlight = (255, 250, 230, 72)
    for y in range(ah):
        for x in range(aw):
            if not grid[y][x]:
                continue
            if y == 0 or not grid[y - 1][x]:
                for dx in range(aw * SCALE):
                    if x * SCALE + dx < w:
                        oy = y * SCALE
                        old = px[x * SCALE + dx, oy]
                        if old[3]:
                            px[x * SCALE + dx, oy] = blend(old, highlight)
            if x == 0 or not grid[y][x - 1]:
                for dy in range(int(SCALE * 0.4) or 1):
                    oy = y * SCALE + dy
                    if oy < h:
                        old = px[0, oy]
                        if old[3]:
                            px[0, oy] = blend(old, highlight)

    return img


def blend(base, over):
    oa = over[3] / 255
    return tuple(int(b * (1 - oa) + o * oa) for b, o in zip(base[:3], over[:3])) + (255,)


def overlay_elder_staff(rows: list[str], facing: str, palette: dict, aw: int, ah: int):
    """Bake elder staff into exported PNG (engine uses overlay at runtime)."""
    from PIL import ImageDraw
    img = render_sprite(rows, palette, aw, ah)
    if facing == "up":
        return img
    col = 27 if facing == "side" else 29
    dr = ImageDraw.Draw(img)
    s = SCALE
    wood = hex_to_rgba(palette.get("staff", "#7a5a36"))
    outline = hex_to_rgba(palette["k"])
    gold = hex_to_rgba(palette["G"])
    x, y0 = col * s, 9 * s
    dr.rectangle([x - s // 2, y0 - s, x + s * 2, y0 + 29 * s], fill=outline)
    dr.rectangle([x, y0, x + s, y0 + 28 * s], fill=wood)
    dr.rectangle([x - s // 2, y0 + 3 * s, x + s * 2, y0 + int(4.4 * s)], fill=gold)
    return img


def save_char(name: str, tpl_set: dict, palette: dict, aw: int, ah: int):
    for facing in ("down", "up", "side"):
        fac = tpl_set.get(facing)
        if not fac or not fac.get("body"):
            continue
        for frame in range(4):
            rows = rows_for_frame(fac, frame)
            if name == "elder":
                img = overlay_elder_staff(rows, facing, palette, aw, ah)
            else:
                img = render_sprite(rows, palette, aw, ah)
            path = OUT / f"char_{name}_{facing}_{frame}.png"
            img.save(path, "PNG")
            print(f"  wrote {path.name} ({img.size[0]}x{img.size[1]})")


# ---------------------------------------------------------------------------
# Tile generators (48x48, seamless)
# ---------------------------------------------------------------------------
def tile_masonry(pal: dict, snow: bool = False) -> "Image.Image":
    from PIL import Image, ImageDraw
    import random
    rng = random.Random(42)
    s = 48
    img = Image.new("RGBA", (s, s), hex_to_rgba(pal["grout"]))
    dr = ImageDraw.Draw(img)
    tones = pal["tones"]
    for by in range(0, s, 8):
        off = 4 if (by // 8) % 2 else 0
        for bx in range(-4, s, 16):
            x0 = bx + off
            t = tones[rng.randint(0, len(tones) - 1)]
            dr.rectangle([x0, by, x0 + 14, by + 6], fill=hex_to_rgba(t))
            dr.rectangle([x0, by, x0 + 14, by + 1], fill=hex_to_rgba(pal["light"]))
            dr.rectangle([x0, by + 5, x0 + 14, by + 6], fill=hex_to_rgba(pal["dark"]))
    if snow:
        for _ in range(6):
            x0, y0 = rng.randint(0, s - 5), rng.randint(0, 6)
            dr.ellipse([x0, y0, x0 + 5, y0 + 3], fill=(232, 237, 245, 180))
    return img


def tile_grass() -> "Image.Image":
    from PIL import Image, ImageDraw
    s = 48
    img = Image.new("RGBA", (s, s), (84, 138, 58, 255))
    dr = ImageDraw.Draw(img)
    for y in range(0, s, 16):
        for x in range(0, s, 16):
            c = (78, 130, 54, 255) if (x + y) % 32 else (84, 138, 58, 255)
            dr.rectangle([x, y, x + 15, y + 15], fill=c)
    for i in range(18):
        x, y = (i * 7) % s, (i * 11) % s
        dr.rectangle([x, y, x + 2, y + 4], fill=(111, 160, 82, 255))
    return img


def tile_path() -> "Image.Image":
    from PIL import Image, ImageDraw
    import random
    rng = random.Random(7)
    s = 48
    base = (168, 140, 100, 255)
    img = Image.new("RGBA", (s, s), base)
    dr = ImageDraw.Draw(img)
    for _ in range(14):
        x, y = rng.randint(0, s - 3), rng.randint(0, s - 3)
        dr.ellipse([x, y, x + 3, y + 2], fill=(140, 115, 80, 255))
    for y in range(0, s, 12):
        dr.line([(0, y), (s, y)], fill=(180, 150, 110, 40), width=1)
    return img


def tile_sand() -> "Image.Image":
    from PIL import Image, ImageDraw
    import random
    rng = random.Random(99)
    s = 48
    img = Image.new("RGBA", (s, s), (194, 148, 90, 255))
    dr = ImageDraw.Draw(img)
    for _ in range(30):
        x, y = rng.randint(0, s), rng.randint(0, s)
        c = 180 + rng.randint(-15, 15)
        dr.point((x, y), fill=(c, c - 30, c - 60, 255))
    for y in range(0, s, 6):
        off = int(3 * (y / 6 % 2))
        dr.arc([off - 8, y, s + off, y + 8], 0, 180, fill=(170, 120, 70, 80))
    return img


def tile_sheol_wall() -> "Image.Image":
    from PIL import Image, ImageDraw
    import random
    rng = random.Random(13)
    pal = {"grout": "#0a0812", "tones": ["#262034", "#2c2540", "#1f1a2c"],
           "light": "#3c3554", "dark": "#120e1c", "moss": "#2a3a48"}
    img = tile_masonry(pal)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(img)
    for _ in range(4):
        x, y = rng.randint(4, 40), rng.randint(4, 40)
        dr.ellipse([x, y, x + 5, y + 3], fill=hex_to_rgba(pal["moss"]))
    return img


def main():
    if not HAS_PIL:
        raise SystemExit("Pillow required: pip install Pillow")

    html = HTML.read_text(encoding="utf-8")
    tpl, hero, pals = parse_js_templates(html)

    print("=== Character sprites ===")
    aw, ah = hero.get("W", 32), hero.get("H", 48)
    save_char("enoch", hero, pals["enoch"], aw, ah)

    for npc in ("edna", "elder", "uriel", "azazel"):
        save_char(npc, tpl, pals[npc], 32, 40)

    print("=== Tile skins ===")
    tiles = {
        "tile_R_hermon.png": tile_masonry(
            {"grout": "#2c2834", "tones": ["#6a6675", "#5c5866", "#787489"],
             "light": "#8e8aa0", "dark": "#3a3642", "moss": "#5c6c46"}, snow=True),
        "tile_#_sheol.png": tile_sheol_wall(),
        "tile_G_earth.png": tile_grass(),
        "tile_P_earth.png": tile_path(),
        "tile_d_dudael.png": tile_sand(),
    }
    for name, im in tiles.items():
        path = OUT / name
        im.save(path, "PNG")
        print(f"  wrote {name} ({im.size[0]}x{im.size[1]})")

    # manifest
    files = sorted(p.name for p in OUT.glob("char_*.png")) + sorted(
        p.name for p in OUT.glob("tile_*.png") if p.name != "tile_preview.png"
    )
    manifest = OUT / "DELIVERY.md"
    lines = ["# ENOCH Asset Delivery\n", f"Generated by `build_assets.py` from engine templates.\n"]
    desc = {
        "char_enoch": "Player Enoch — 32:48 (128×192), transparent PNG, engine palette",
        "char_edna": "Edna — purple-robed wife, 32:40 (128×160)",
        "char_elder": "Valley elder — grey robe, staff, 32:40",
        "char_uriel": "Uriel — white-gold angel, 32:40",
        "char_azazel": "Azazel — black robe, gold trim, 32:40",
        "tile_R_hermon": "Hermon masonry wall tile, 48×48, snow dust",
        "tile_#_sheol": "Sheol catacomb brick, 48×48",
        "tile_G_earth": "Jared's Valley grass, 48×48",
        "tile_P_earth": "Packed dirt path, 48×48",
        "tile_d_dudael": "Dudael desert sand, 48×48",
    }
    for f in files:
        key = "_".join(f.replace(".png", "").split("_")[:3])
        if f.startswith("tile_"):
            key = f.replace(".png", "")
        note = next((v for k, v in desc.items() if f.startswith(k.replace("_", "_")) or f.startswith(k)), "")
        for k, v in desc.items():
            if f.startswith(k):
                note = v
                break
        lines.append(f"- `{f}` — {note}")
    lines.append("\n## Registration (engine owner)\n")
    lines.append("```js")
    for f in files:
        if f.startswith("char_"):
            parts = f.replace(".png", "").split("_")
            # char_enoch_down_0 -> char:enoch:down:0
            pal, facing, frame = parts[1], parts[2], parts[3]
            lines.append(f"ASSETS.register('char:{pal}:{facing}:{frame}','assets/{f}');")
        elif f.startswith("tile_"):
            # tile_R_hermon -> tile:R:hermon
            parts = f.replace(".png", "").split("_")
            ch, mmap = parts[1], parts[2]
            lines.append(f"ASSETS.register('tile:{ch}:{mmap}','assets/{f}');")
    lines.append("```\n")
    manifest.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {manifest} ({len(files)} assets)")


if __name__ == "__main__":
    main()