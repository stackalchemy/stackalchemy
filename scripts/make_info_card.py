from pathlib import Path
import os
import html


OUT = Path("info-card.svg")
STATIC = os.getenv("STATIC") == "1"

ROWS = [
    ("Now", "CSE • Full-stack developer in progress"),
    ("Prev", "HTML • CSS • JavaScript • React"),
    ("Stack", "Java • Spring • MySQL • Git • GitHub"),
    ("Build", "Parkash Paints • Oolkar • coding projects"),
    ("Focus", "Backend engineering + placements"),
]


def main() -> None:
    row_height = 48
    height = 76 + row_height * len(ROWS)
    anim_attr = "" if STATIC else 'opacity="0"'
    parts = []

    for i, (key, value) in enumerate(ROWS):
        y = 76 + i * row_height
        delay = i * 0.12
        animation = "" if STATIC else (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.24s" '
            f'begin="{delay:.2f}s" fill="freeze"/>'
        )
        parts.append(
            f'<g {anim_attr}>'
            f'<text x="28" y="{y}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" '
            f'font-size="15" fill="#58a6ff">{html.escape(key)}</text>'
            f'<text x="118" y="{y}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" '
            f'font-size="14" fill="#c9d1d9">{html.escape(value)}</text>'
            f'<line x1="28" y1="{y+12}" x2="462" y2="{y+12}" stroke="#21262d"/>'
            f'{animation}</g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="{height}" viewBox="0 0 490 {height}">
  <rect width="490" height="{height}" rx="12" fill="#0d1117"/>
  <rect x="1" y="1" width="488" height="{height-2}" rx="11" fill="none" stroke="#30363d"/>
  <circle cx="24" cy="24" r="6" fill="#ff7b72"/>
  <circle cx="46" cy="24" r="6" fill="#d29922"/>
  <circle cx="68" cy="24" r="6" fill="#3fb950"/>
  <text x="28" y="54" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="14" fill="#8b949e">stackalchemy@github:~$ neofetch</text>
  {''.join(parts)}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
