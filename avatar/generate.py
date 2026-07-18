#!/usr/bin/env python3
"""Генератор SVG аватара: кольцо с ядром, каналы кромками, глитч-нарезка.

Пишет <палитра>.svg для каждой палитры из PALETTES и preview.html для выбора;
PNG и очистка - в Makefile.
"""

import base64
import pathlib

# роли каналов: up/left/right - направление сдвига копии под глифом цвета base;
# base и background опциональны, по умолчанию BASE и BACKGROUND
PALETTES = {
    "disc": {"up": "#F8F32B", "left": "#FF2A6D", "right": "#00E5D4"},
    "rgb": {"up": "#2979FF", "left": "#FF3B30", "right": "#00E676"},
    "acid": {"up": "#FF6D00", "left": "#7C4DFF", "right": "#9EF01A"},
    "ember": {"up": "#FFB000", "left": "#FF3D00", "right": "#00BFA5"},
    "cold": {"up": "#00E5A0", "left": "#7C4DFF", "right": "#4FC3F7"},
    "gruvbox": {
        "up": "#FABD2F", "left": "#FB4934", "right": "#8EC07C",
        "base": "#EBDBB2", "background": "#282828",
    },
    "gruvbox-mix": {
        "up": "#FE8019", "left": "#D3869B", "right": "#83A598",
        "base": "#FBF1C7", "background": "#1D2021",
    },
    "habamax": {
        "up": "#FFAF5F", "left": "#D75F87", "right": "#87AFAF",
        "base": "#C7C7C7", "background": "#1C1C1C",
    },
    "habamax-cool": {
        "up": "#87AFAF", "left": "#AF87AF", "right": "#5FAF5F",
        "base": "#C7C7C7", "background": "#1C1C1C",
    },
}

BASE = "#E8E8E6"
BACKGROUND = "#050505"

# (y, высота, сдвиг по x); полосы обязаны покрывать 0..1024 без зазоров
BANDS = [
    (0, 160, 0), (160, 70, -60), (230, 60, 30), (290, 100, 0), (390, 70, 90),
    (460, 80, -40), (540, 70, 0), (610, 80, -90), (690, 90, 44), (780, 244, 0),
]

# (x, y, w, h, роль цвета, прозрачность)
NOISE = [
    (120, 270, 90, 8, "left", "0.85"),
    (790, 330, 120, 8, "right", "0.85"),
    (660, 880, 100, 8, "up", "0.85"),
    (180, 740, 66, 6, "white", "0.5"),
    (840, 600, 100, 6, "left", "0.7"),
    (420, 96, 150, 8, "right", "0.7"),
]


def render_svg(palette):
    base = palette.get("base", BASE)
    background = palette.get("background", BACKGROUND)
    color = {**palette, "white": "#FFFFFF"}
    clips = "\n".join(
        f'    <clipPath id="c{i}"><rect x="-300" y="{y}" width="1624" height="{h}"/></clipPath>'
        for i, (y, h, _) in enumerate(BANDS, 1)
    )
    slices = "\n".join(
        f'  <g clip-path="url(#c{i})"><g><use href="#stack"/></g></g>'
        if dx == 0 else
        f'  <g clip-path="url(#c{i})"><g transform="translate({dx} 0)"><use href="#stack"/></g></g>'
        for i, (_, _, dx) in enumerate(BANDS, 1)
    )
    noise = "\n".join(
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color[role]}" opacity="{op}"/>'
        for x, y, w, h, role, op in NOISE
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <defs>
    <g id="glyph">
      <circle cx="512" cy="500" r="280" fill="none" stroke-width="88"/>
      <circle cx="512" cy="500" r="60" stroke="none"/>
    </g>
    <g id="stack">
      <use href="#glyph" transform="translate(0 -26)" stroke="{palette["up"]}" fill="{palette["up"]}"/>
      <use href="#glyph" transform="translate(-30 8)" stroke="{palette["left"]}" fill="{palette["left"]}"/>
      <use href="#glyph" transform="translate(28 12)" stroke="{palette["right"]}" fill="{palette["right"]}"/>
      <use href="#glyph" stroke="{base}" fill="{base}"/>
    </g>
    <pattern id="scan" patternUnits="userSpaceOnUse" width="8" height="6">
      <rect width="8" height="2.6" fill="#000000"/>
    </pattern>
{clips}
  </defs>
  <rect width="1024" height="1024" fill="{background}"/>
{slices}
{noise}
  <rect width="1024" height="1024" fill="url(#scan)" opacity="0.3"/>
</svg>
'''


PREVIEW_CSS = '''\
:root { --bg: #131311; --ink: #cfcbc2; --mut: #87837b; --line: #2a2a27; }
* { box-sizing: border-box; margin: 0; }
body {
  background: var(--bg); color: var(--ink);
  font: 14px/1.5 ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  padding: 28px clamp(16px, 4vw, 48px) 64px;
}
header { max-width: 1200px; margin: 0 auto 24px; }
h1 { font-size: 16px; font-weight: 600; letter-spacing: 0.05em; }
.status { color: var(--mut); font-size: 13px; margin-top: 6px; }
.status b { color: var(--ink); font-weight: 600; }
.grid {
  max-width: 1200px; margin: 0 auto; display: grid; gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}
.card {
  border: 1px solid var(--line); border-radius: 6px; padding: 14px;
  display: flex; flex-direction: column; gap: 12px; cursor: pointer;
}
.card:focus-visible { outline: 1px dashed var(--mut); outline-offset: 3px; }
.card.sel { box-shadow: 0 0 0 2px var(--ring); border-color: transparent; }
img { display: block; max-width: 100%; }
.master { width: 100%; height: auto; border-radius: 6px; }
.crops { display: flex; align-items: center; gap: 14px; }
.crops img { border-radius: 50%; }
figcaption { display: flex; justify-content: space-between; align-items: center; }
.name { font-size: 13px; letter-spacing: 0.04em; }
.dots i {
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  margin-left: 6px;
}
'''

PREVIEW_JS = '''\
for (const card of document.querySelectorAll(".card")) {
  const pick = () => {
    document.querySelectorAll(".card.sel").forEach(c => c.classList.remove("sel"));
    card.classList.add("sel");
    document.getElementById("picked").textContent = card.dataset.name;
  };
  card.addEventListener("click", pick);
  card.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
  });
}
'''


def render_preview(svgs):
    cards = []
    for name, svg in svgs.items():
        p = PALETTES[name]
        uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
        dots = "".join(f'<i style="background:{p[r]}"></i>' for r in ("up", "left", "right"))
        cards.append(f'''\
  <figure class="card" data-name="{name}" tabindex="0" style="--ring:{p["up"]}">
    <img class="master" src="{uri}" alt="{name}" width="1024" height="1024">
    <div class="crops">
      <img src="{uri}" alt="" width="88" height="88">
      <img src="{uri}" alt="" width="40" height="40">
      <img src="{uri}" alt="" width="20" height="20">
    </div>
    <figcaption><span class="name">{name}</span><span class="dots">{dots}</span></figcaption>
  </figure>''')
    body = '''<header>
  <h1>аватар - выбор палитры</h1>
  <p class="status">кропы 88 / 40 / 20 px - контексты GitHub; клик или Enter - выбор;
  выбрано: <b id="picked" aria-live="polite">-</b></p>
</header>
<div class="grid">
{cards}
</div>'''.format(cards="\n".join(cards))
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>avatar palettes</title>
<style>
{PREVIEW_CSS}</style>
</head>
<body>
{body}
<script>
{PREVIEW_JS}</script>
</body>
</html>
'''


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    svgs = {name: render_svg(PALETTES[name]) for name in sorted(PALETTES)}
    for name, svg in svgs.items():
        (here / f"{name}.svg").write_text(svg)
        print(f"written: {name}.svg")
    (here / "preview.html").write_text(render_preview(svgs))
    print("written: preview.html")
