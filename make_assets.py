#!/usr/bin/env python3
"""Generate every graphic on this profile from real data.

Nothing here is embedded from a third-party server. Badge and stat-card
services rate-limit, go down, change their rendering without telling you, and
see the traffic of everyone who visits. A page that opens by claiming to care
about dependencies should not have ten of them above the fold.

So: plain SVG, written here, committed. GitHub serves it.

    python3 tools/refresh.py     # pull fresh numbers from the GitHub API
    python3 tools/make_assets.py # redraw

Fonts are the viewer's own monospace stack, because GitHub strips <style>
blocks from README SVGs and a subsetted webfont is a lot of binary to carry
for a heading.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
DATA = ROOT / "data"

VOID = "#0a0c11"
LINE = "#1c2330"
DIM = "#67748a"
TEXT = "#c9d1dd"
BRIGHT = "#e8edf5"
EMBER = "#ff7a45"

MONO = (
    "ui-monospace,SFMono-Regular,'SF Mono','JetBrains Mono',"
    "Menlo,Consolas,'DejaVu Sans Mono',monospace"
)
W = 860


def _load(name, fallback):
    try:
        return json.loads((DATA / name).read_text())
    except Exception:
        return fallback


def banner(title: str, subtitle: str) -> str:
    """Contribution total, and a year of activity as one line.

    The sparkline is the point: a number says how much, a shape says when, and
    the shape is the part that shows something changing.
    """
    stats = _load("stats.json", {})
    total = stats.get("total", 0)
    weekly = stats.get("weekly", [0] * 52)
    peak = max(weekly) or 1

    # The sparkline gets its own band below the number. Drawn over the same
    # rows it ran straight through the label, which is the kind of thing that
    # only shows up once you render it.
    base, amp = 168.0, 34.0
    step = (W - 80) / max(len(weekly), 1)
    pts = []
    for i, v in enumerate(weekly):
        x = 40 + i * step
        y = base - (v / peak) * amp
        pts.append(f"{x:.1f},{y:.1f}")
    spark = " ".join(pts)

    H = 208
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}. {total} contributions in the last year.">
  <rect width="{W}" height="{H}" rx="4" fill="{VOID}"/>
  <rect width="{W}" height="3" fill="{EMBER}"/>
  <text x="40" y="54" font-family="{MONO}" font-size="24" font-weight="700" fill="{BRIGHT}">{title}</text>
  <text x="40" y="78" font-family="{MONO}" font-size="13" fill="{DIM}">{subtitle}</text>
  <text x="40" y="124" font-family="{MONO}" font-size="34" font-weight="700" fill="{BRIGHT}">{total}</text>
  <text x="{40 + 21 * len(str(total))}" y="124" font-family="{MONO}" font-size="12" fill="{DIM}">contributions in the last year</text>
  <text x="{W - 40}" y="124" font-family="{MONO}" font-size="12" fill="{DIM}" text-anchor="end">{stats.get('active_days', 0)} active days  ·  best week {stats.get('best_week', 0)}</text>
  <polyline points="{spark}" fill="none" stroke="{EMBER}" stroke-width="1.6" opacity="0.9"/>
  <line x1="40" y1="{base:.0f}" x2="{W - 40}" y2="{base:.0f}" stroke="{LINE}" stroke-width="1"/>
</svg>
"""


def section(label: str) -> str:
    """A section rule, the way a CLI delimits its own output."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="26" viewBox="0 0 {W} 26" role="img" aria-label="{label}">
  <text x="0" y="17" font-family="{MONO}" font-size="12" font-weight="700" fill="{EMBER}">{label}</text>
  <line x1="{len(label) * 7.4 + 14}" y1="12" x2="{W}" y2="12" stroke="{LINE}" stroke-width="1"/>
</svg>
"""


def stats_panel() -> str:
    """What the year actually looked like, by language and by week."""
    langs = _load("languages.json", {})
    total_bytes = sum(langs.values()) or 1
    rows = list(langs.items())[:6]

    body, y = [], 78
    for name, val in rows:
        pct = 100 * val / total_bytes
        bar = int((pct / 100) * 300)
        body.append(
            f'<text x="24" y="{y}" font-family="{MONO}" font-size="12" fill="{TEXT}">{name.lower()}</text>'
            f'<rect x="150" y="{y - 9}" width="{bar}" height="8" fill="{EMBER}" opacity="0.85" rx="1"/>'
            f'<text x="470" y="{y}" font-family="{MONO}" font-size="12" fill="{DIM}" text-anchor="end">{pct:.0f}%</text>'
        )
        y += 24

    stats = _load("stats.json", {})
    right = [
        ("current streak", f"{stats.get('current_streak', 0)} days"),
        ("longest streak", f"{stats.get('longest_streak', 0)} days"),
        ("active days", f"{stats.get('active_days', 0)} / 365"),
        ("public repos", str(stats.get("public_repos", 0))),
    ]
    ry = 78
    for label, val in right:
        body.append(
            f'<text x="530" y="{ry}" font-family="{MONO}" font-size="12" fill="{DIM}">{label}</text>'
            f'<text x="{W - 24}" y="{ry}" font-family="{MONO}" font-size="12" font-weight="700" fill="{BRIGHT}" text-anchor="end">{val}</text>'
        )
        ry += 24

    height = max(y, ry) + 16
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Language and activity statistics">
  <rect width="{W}" height="{height}" rx="4" fill="{VOID}" stroke="{LINE}" stroke-width="1"/>
  <text x="24" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{DIM}">BY BYTES WRITTEN</text>
  <text x="530" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{DIM}">THE YEAR</text>
  <line x1="20" y1="48" x2="{W - 20}" y2="48" stroke="{LINE}" stroke-width="1"/>
  {"".join(body)}
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(
        banner("harshavardhan beesabathina", "systems and agent infrastructure · tirupati, india")
    )
    (OUT / "header-antharmaya.svg").write_text(
        banner("antharmaya labs", "agent and systems infrastructure · india")
    )
    for name in ("about", "stack", "projects", "stats", "about-this-page"):
        (OUT / f"s-{name}.svg").write_text(section(name.replace("-", " ")))
    (OUT / "stats.svg").write_text(stats_panel())
    print(f"wrote {len(list(OUT.glob('*.svg')))} svg files")


if __name__ == "__main__":
    main()
