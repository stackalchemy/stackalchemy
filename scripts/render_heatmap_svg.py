from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path


DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]

CELL = 12
GAP = 3
LEFT = 44
TOP = 34
ROWS = 7
COLS = 53
GRID_W = COLS * CELL + (COLS - 1) * GAP
GRID_H = ROWS * CELL + (ROWS - 1) * GAP
WIDTH = LEFT + GRID_W + 20
HEIGHT = TOP + GRID_H + 72


def escape(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def week_sunday(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def build_grid(days):
    values = {date.fromisoformat(x["date"]): x["level"] for x in days}
    counts = {date.fromisoformat(x["date"]): x["count"] for x in days}
    available = sorted(values)
    if not available:
        return [], counts

    last_sunday = week_sunday(available[-1])
    first_sunday = last_sunday - timedelta(weeks=COLS - 1)

    grid = []
    for col in range(COLS):
        start = first_sunday + timedelta(weeks=col)
        for row in range(ROWS):
            d = start + timedelta(days=row)
            grid.append((col, row, d, values.get(d, 0)))
    return grid, counts


def main() -> None:
    if not DATA.exists():
        raise SystemExit("data/contributions.json is missing. Run fetch_contributions.py first.")

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    grid, counts = build_grid(payload["days"])

    rects = []
    for col, row, day, level in grid:
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        delay = (col * 7 + row) * 0.012
        fill = PALETTE[level]
        title = f'{payload["username"]} • {day.isoformat()} • {counts.get(day, 0)} contributions'
        rects.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}">'
            f'<title>{escape(title)}</title>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.16s" '
            f'begin="{delay:.3f}s" fill="freeze"/>'
            f'</rect>'
        )

    total = f'{payload["total"]:,}'
    footer = (
        f'current streak: {payload["current_streak"]} days   •   '
        f'longest: {payload["longest_streak"]} days   •   '
        f'best day: {payload["best_day"]["count"]:,}'
    )

    legend = []
    legend_y = TOP + GRID_H + 30
    for i, label in enumerate(["Less", "", "", "", "", "More"]):
        x = LEFT + 42 + i * 18
        if label:
            legend.append(
                f'<text x="{x-28}" y="{legend_y+10}" font-family="ui-monospace,monospace" '
                f'font-size="11" fill="#8b949e">{label}</text>'
            )
        legend.append(
            f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[i]}"/>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="100%" height="100%" rx="12" fill="#0d1117"/>
  <rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="11" fill="none" stroke="#30363d"/>
  <text x="{LEFT}" y="20" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="14" fill="#c9d1d9">stackalchemy@github:~$ ./contributions.sh</text>
  <text x="{LEFT}" y="32" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="12" fill="#8b949e">{total} contributions in the last year</text>
  {''.join(rects)}
  {''.join(legend)}
  <text x="{LEFT}" y="{HEIGHT-12}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="11" fill="#8b949e">{escape(footer)}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
