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
    match = re.search(r"(\\d[\\d,]*)", text.replace("\\xa0", " "))
    return int(match.group(1).replace(",", "")) if match else 0


def main() -> None:
    response = requests.get(
        URL,
        headers={"User-Agent": "stackalchemy-profile-art/1.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("[data-date][data-level]")

    if not cells:
        raise RuntimeError("GitHub contribution cells were not found.")

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

        label = cell.get("aria-label", "")
        days.append({
            "date": day.isoformat(),
            "count": parse_count(label),
            "level": max(0, min(5, level)),
        })

    days.sort(key=lambda x: x["date"])

    # Remove accidental duplicates while preserving the latest parsed value.
    unique = {}
    for item in days:
        unique[item["date"]] = item
    days = [unique[k] for k in sorted(unique)]

    contribution_days = [d for d in days if d["count"] > 0]

    current_streak = 0
    cursor = date.today()
    by_date = {date.fromisoformat(d["date"]): d["count"] for d in days}

    # A contribution graph can lag the current day. Start from the newest
    # available day instead of assuming today's cell exists.
    if by_date:
        cursor = min(max(by_date), date.today())

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
    print(f"Wrote {OUT} ({len(days)} days)")


if __name__ == "__main__":
    main()
