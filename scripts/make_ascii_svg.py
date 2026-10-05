from pathlib import Path
import math

import numpy as np
from PIL import Image


RAMP = " .`:-=+*cs#%@"
IMG = Path("source-prepped.png")
OUT = Path("avi-ascii.svg")

COLS = 100
ROWS = 53
FONT_SIZE = 8
CHAR_W = 5.8
LINE_H = 8.5


def esc(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def main() -> None:
    if not IMG.exists():
        raise SystemExit(
            "source-prepped.png is missing. Run: python scripts/prep_photo.py source-photo.jpg"
        )

    image = Image.open(IMG).convert("L")
    # Match the target aspect ratio of monospace characters.
    image = image.resize((COLS, ROWS))
    data = np.asarray(image)

    width = COLS * CHAR_W + 20
    height = ROWS * LINE_H + 20

    groups = []
    for r in range(ROWS):
        y = 14 + r * LINE_H
        chars = []
        for c in range(COLS):
            brightness = int(data[r, c])
            idx = int(round((255 - brightness) / 255 * (len(RAMP) - 1)))
            glyph = RAMP[max(0, min(len(RAMP) - 1, idx))]
            chars.append(glyph)
        line = esc("".join(chars).rstrip())
        delay = r * 0.055
        groups.append(
            f'<g opacity="0"><text x="10" y="{y:.1f}" '
            f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" '
            f'font-size="{FONT_SIZE}px" fill="#c9d1d9" xml:space="preserve">'
            f'{line}</text>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.08s" '
            f'begin="{delay:.3f}s" fill="freeze"/></g>'
        )

    total = ROWS * 0.055 + 0.2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">
  <rect width="100%" height="100%" rx="12" fill="#0d1117"/>
  <rect x="1" y="1" width="{width-2:.0f}" height="{height-2:.0f}" rx="11" fill="none" stroke="#30363d"/>
  {''.join(groups)}
  <rect x="10" y="{height-10:.1f}" width="{max(8, FONT_SIZE/2):.1f}" height="2" fill="#58a6ff">
    <animate attributeName="x" from="10" to="{width-10:.1f}" dur="0.5s" begin="0s" fill="freeze"/>
    <animate attributeName="opacity" from="1" to="0" dur="0.15s" begin="{total:.3f}s" fill="freeze"/>
  </rect>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
