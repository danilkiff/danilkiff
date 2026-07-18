#!/usr/bin/env python3
"""Генератор SVG аватара: кольцо с ядром, каналы кромками, глитч-нарезка.

Пишет <палитра>.svg для каждой палитры из PALETTES; PNG и очистка - в Makefile.
"""

import pathlib

# роли каналов: up/left/right - направление сдвига копии под белым глифом
PALETTES = {
    "disc": {"up": "#F8F32B", "left": "#FF2A6D", "right": "#00E5D4"},
    "rgb": {"up": "#2979FF", "left": "#FF3B30", "right": "#00E676"},
    "acid": {"up": "#FF6D00", "left": "#7C4DFF", "right": "#9EF01A"},
    "ember": {"up": "#FFB000", "left": "#FF3D00", "right": "#00BFA5"},
    "cold": {"up": "#00E5A0", "left": "#7C4DFF", "right": "#4FC3F7"},
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
      <use href="#glyph" stroke="{BASE}" fill="{BASE}"/>
    </g>
    <pattern id="scan" patternUnits="userSpaceOnUse" width="8" height="6">
      <rect width="8" height="2.6" fill="#000000"/>
    </pattern>
{clips}
  </defs>
  <rect width="1024" height="1024" fill="{BACKGROUND}"/>
{slices}
{noise}
  <rect width="1024" height="1024" fill="url(#scan)" opacity="0.3"/>
</svg>
'''


if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    for name in sorted(PALETTES):
        (here / f"{name}.svg").write_text(render_svg(PALETTES[name]))
        print(f"written: {name}.svg")
