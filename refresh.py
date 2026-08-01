#!/usr/bin/env python3
"""Pull the numbers this page shows, straight from the GitHub API.

Separate from drawing, so a rate limit or a network failure leaves the last
good data in place rather than a page of zeros. Run it, commit whatever
actually changed, then redraw.

    python3 tools/refresh.py && python3 tools/make_assets.py
"""

import collections
import datetime
import json
import subprocess
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
OWNERS = ("varbees", "antharmaya")

CONTRIB_QUERY = """
{
  viewer {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True).stdout


def contributions() -> dict:
    raw = json.loads(gh("api", "graphql", "-f", f"query={CONTRIB_QUERY}"))
    cal = raw["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    today = datetime.date.today()

    # Streak walks backwards from the most recent day that has happened. The
    # calendar includes future days in the current week, and counting those as
    # a break would zero a live streak every Monday.
    streak = 0
    for d in reversed(days):
        if datetime.date.fromisoformat(d["date"]) > today:
            continue
        if d["contributionCount"] > 0:
            streak += 1
        else:
            break

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)

    # Keep the per-day grid, not just weekly sums: the ascii calendar needs
    # weekday position, and a week total cannot be un-summed back into days.
    grid = []
    for w in weeks:
        col = [0] * 7
        for d in w["contributionDays"]:
            col[datetime.date.fromisoformat(d["date"]).weekday()] = d["contributionCount"]
        grid.append(col)

    months = []
    seen = set()
    for i, w in enumerate(weeks):
        first = datetime.date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month not in seen:
            seen.add(first.month)
            months.append([i, first.strftime("%b").lower()])

    return {
        "grid": grid,
        "months": months,
        "total": cal["totalContributions"],
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
        "best_week": max(sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks),
        "current_streak": streak,
        "longest_streak": longest,
        "weekly": [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks],
    }


def languages() -> tuple[dict, int]:
    """Bytes written per language across public, non-fork repositories."""
    totals: collections.Counter = collections.Counter()
    count = 0
    for owner in OWNERS:
        path = f"users/{owner}/repos" if owner == "varbees" else f"orgs/{owner}/repos"
        repos = json.loads(gh("api", f"{path}?per_page=100", "--paginate") or "[]")
        for r in repos:
            if r.get("fork") or r.get("private"):
                continue
            count += 1
            langs = json.loads(gh("api", f"repos/{r['full_name']}/languages") or "{}")
            totals.update(langs)
    # Markup and styling are not the point of this page.
    for noise in ("HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Batchfile"):
        totals.pop(noise, None)
    return dict(totals.most_common(10)), count


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    stats = contributions()
    langs, repo_count = languages()
    stats["public_repos"] = repo_count

    (DATA / "stats.json").write_text(json.dumps(stats, indent=1))
    (DATA / "languages.json").write_text(json.dumps(langs, indent=1))
    print(
        f"{stats['total']} contributions · {stats['active_days']} active days · "
        f"streak {stats['current_streak']}/{stats['longest_streak']} · {repo_count} public repos"
    )


if __name__ == "__main__":
    main()
