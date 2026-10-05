from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import re

import requests
from bs4 import BeautifulSoup


USERNAME = "stackalchemy"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def parse_count(text: str) -> int:
    match = re.search(r"(\d[\d,]*)", text.replace("\xa0", " "))
    return int(match.group(1).replace(",", "")) if match else 0


def main() -> None:
    response = requests.get(
        URL,
        headers={"User-Agent": "stackalchemy-profile-art/1.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select(".ContributionCalendar-day[data-date][data-level]")
    if not cells:
        cells = soup.select("[data-date][data-level]")
    if not cells:
        raise RuntimeError("GitHub contribution cells were not found.")

    # GitHub has used different tooltip layouts over time. Recent markup
    # keeps counts in <tool-tip for="CELL_ID">...</tool-tip>; older markup
    # sometimes stores the count directly in title/aria-label.
    tooltip_by_id = {}
    for tooltip in soup.select("tool-tip[for]"):
        target = tooltip.get("for")
        if target:
            tooltip_by_id[target] = tooltip.get_text(" ", strip=True)

    days = []
    for cell in cells:
        raw_date = cell.get("data-date")
        raw_level = cell.get("data-level", "0")
        if not raw_date:
            continue

        try:
            day = date.fromisoformat(raw_date)
            level = int(raw_level)
        except ValueError:
            continue

        label = cell.get("title", "") or cell.get("aria-label", "")
        if not label:
            cell_id = cell.get("id")
            if cell_id:
                label = tooltip_by_id.get(cell_id, "")
        if not label:
            tooltip = cell.find("tool-tip")
            if tooltip:
                label = tooltip.get_text(" ", strip=True)

        days.append({
            "date": day.isoformat(),
            "count": parse_count(label),
            "level": max(0, min(5, level)),
        })

    unique = {item["date"]: item for item in days}
    days = [unique[k] for k in sorted(unique)]

    contribution_days = [d for d in days if d["count"] > 0]
    by_date = {date.fromisoformat(d["date"]): d["count"] for d in days}

    current_streak = 0
    if by_date:
        cursor = min(max(by_date), date.today())
        while by_date.get(cursor, 0) == 0 and cursor > min(by_date):
            cursor -= timedelta(days=1)
        while by_date.get(cursor, 0) > 0:
            current_streak += 1
            cursor -= timedelta(days=1)

    longest_streak = 0
    running = 0
    previous = None
    for item in contribution_days:
        current = date.fromisoformat(item["date"])
        if previous and current == previous + timedelta(days=1):
            running += 1
        else:
            running = 1
        longest_streak = max(longest_streak, running)
        previous = current

    best_day = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})

    monthly = defaultdict(int)
    for item in days:
        monthly[item["date"][:7]] += item["count"]

    payload = {
        "username": USERNAME,
        "generated_at": date.today().isoformat(),
        "days": days,
        "total": sum(d["count"] for d in days),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(days)} days, {payload['total']} contributions)")


if __name__ == "__main__":
    main()
