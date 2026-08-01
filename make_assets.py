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

# PhotoSelect's system, converted from its oklch tokens. Paper and ink with one
# blue accent — the same palette the products use, so the profile, the sites
# and the tools read as one thing rather than three.
#
# Both themes are drawn. GitHub honours prefers-color-scheme inside <picture>,
# and a light panel on a dark profile is a glaring white rectangle. Choosing
# one theme means choosing which half of readers get the bad version.
THEMES = {
    "light": dict(
        PAPER="#fafcfe",  # --background  oklch(0.99 0.003 250)
        CARD="#ffffff",   # --card
        LINE="#e6ebf0",   # --border      oklch(0.92 0.005 250)
        DIM="#5e646a",    # --muted-fg    oklch(0.50 0.012 250)
        INK="#0e1216",    # --foreground  oklch(0.18 0.010 250)
        BLUE="#004fa7",   # --primary     oklch(0.44 0.16 255)
    ),
    "dark": dict(
        PAPER="#0d1117",  # GitHub's own dark canvas, so the card does not float
        CARD="#0d1117",
        LINE="#232b34",
        DIM="#8b949e",
        INK="#e8edf3",
        BLUE="#589bff",   # the same hue, lifted for contrast on dark
    ),
}
T = THEMES["light"]

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
  <rect width="{W}" height="{H}" rx="4" fill="{T["PAPER"]}" stroke="{T["LINE"]}" stroke-width="1"/>
  <rect width="{W}" height="3" fill="{T["BLUE"]}"/>
  <text x="40" y="54" font-family="{MONO}" font-size="24" font-weight="700" fill="{T["INK"]}">{title}</text>
  <text x="40" y="78" font-family="{MONO}" font-size="13" fill="{T["DIM"]}">{subtitle}</text>
  <text x="40" y="124" font-family="{MONO}" font-size="34" font-weight="700" fill="{T["INK"]}">{total}</text>
  <text x="{40 + 21 * len(str(total))}" y="124" font-family="{MONO}" font-size="12" fill="{T["DIM"]}">contributions in the last year</text>
  <text x="{W - 40}" y="124" font-family="{MONO}" font-size="12" fill="{T["DIM"]}" text-anchor="end">{stats.get('active_days', 0)} active days  ·  best week {stats.get('best_week', 0)}</text>
  <polyline points="{spark}" fill="none" stroke="{T["BLUE"]}" stroke-width="1.6" opacity="0.95"/>
  <line x1="40" y1="{base:.0f}" x2="{W - 40}" y2="{base:.0f}" stroke="{T["LINE"]}" stroke-width="1"/>
</svg>
"""


def section(label: str) -> str:
    """A section rule, the way a CLI delimits its own output."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="26" viewBox="0 0 {W} 26" role="img" aria-label="{label}">
  <text x="0" y="17" font-family="{MONO}" font-size="12" font-weight="700" fill="{T["BLUE"]}">{label}</text>
  <line x1="{len(label) * 7.4 + 14}" y1="12" x2="{W}" y2="12" stroke="{T["LINE"]}" stroke-width="1"/>
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
            f'<text x="24" y="{y}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}">{name.lower()}</text>'
            f'<rect x="150" y="{y - 9}" width="{bar}" height="8" fill="{T["BLUE"]}" opacity="0.9" rx="1"/>'
            f'<text x="470" y="{y}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}" text-anchor="end">{pct:.0f}%</text>'
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
            f'<text x="530" y="{ry}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}">{label}</text>'
            f'<text x="{W - 24}" y="{ry}" font-family="{MONO}" font-size="12" font-weight="700" fill="{T["INK"]}" text-anchor="end">{val}</text>'
        )
        ry += 24

    height = max(y, ry) + 16
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Language and activity statistics">
  <rect width="{W}" height="{height}" rx="4" fill="{T["CARD"]}" stroke="{T["LINE"]}" stroke-width="1"/>
  <text x="24" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{T["DIM"]}">BY BYTES WRITTEN</text>
  <text x="530" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{T["DIM"]}">THE YEAR</text>
  <line x1="20" y1="48" x2="{W - 20}" y2="48" stroke="{T["LINE"]}" stroke-width="1"/>
  {"".join(body)}
</svg>
"""


def main() -> None:
    global T
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, palette in THEMES.items():
        T = palette
        suffix = f"-{theme}"
        (OUT / f"header{suffix}.svg").write_text(
            banner("harshavardhan beesabathina", "systems and agent infrastructure · tirupati, india")
        )
        (OUT / f"header-antharmaya{suffix}.svg").write_text(
            banner("antharmaya labs", "agent and systems infrastructure · india")
        )
        for name in ("about", "stack", "projects", "stats", "about-this-page"):
            (OUT / f"s-{name}{suffix}.svg").write_text(section(name.replace("-", " ")))
        (OUT / f"stats{suffix}.svg").write_text(stats_panel())
    print(f"wrote {len(list(OUT.glob('*.svg')))} svg files (light + dark)")


if __name__ == "__main__":
    main()
