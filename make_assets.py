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

W = 860
MONO = (
    "ui-monospace,SFMono-Regular,'SF Mono','JetBrains Mono',"
    "Menlo,Consolas,'DejaVu Sans Mono',monospace"
)

# PhotoSelect's system, converted from its oklch tokens. Paper and ink with one
# blue — the same palette the products use, so the profile, the sites and the
# tools read as one system rather than three.
#
# Both themes are drawn and selected by prefers-color-scheme. A light panel on
# a dark profile is a glaring white rectangle, so shipping one theme means
# choosing which half of readers get the bad version.
#
# RAMP is five steps of that one blue, darkest for the busiest day. A heatmap
# needs shades to be readable at a glance; a single colour turns a year into
# undifferentiated texture.
THEMES = {
    "light": dict(
        PAPER="#fafcfe",  # --background  oklch(0.99 0.003 250)
        CARD="#ffffff",
        LINE="#e6ebf0",  # --border      oklch(0.92 0.005 250)
        DIM="#5e646a",  # --muted-fg    oklch(0.50 0.012 250)
        INK="#0e1216",  # --foreground  oklch(0.18 0.010 250)
        BLUE="#004fa7",  # --primary     oklch(0.44 0.16 255)
        RAMP=["#dde5ee", "#a9c5e5", "#6a9ed8", "#2a6cb8", "#004fa7"],
    ),
    "dark": dict(
        PAPER="#0d1117",  # GitHub's own dark canvas, so panels sit flush
        CARD="#0d1117",
        LINE="#232b34",
        DIM="#8b949e",
        INK="#e8edf3",
        BLUE="#589bff",  # the same hue, lifted for contrast on dark
        RAMP=["#1c222b", "#1f4b7a", "#2f6fb5", "#4a90e2", "#79b8ff"],
    ),
}
T = THEMES["light"]


def _load(name, fallback):
    try:
        return json.loads((DATA / name).read_text())
    except Exception:
        return fallback


def banner(title: str, subtitle: str) -> str:
    """Contribution total, with the year as one line.

    A number says how much; the shape says when. The shape is the part that
    shows something changing.
    """
    st = _load("stats.json", {})
    total = st.get("total", 0)
    weekly = st.get("weekly", [0] * 52)
    peak = max(weekly) or 1

    # The sparkline gets its own band below the number. Drawn across the same
    # rows it ran straight through the label, which only showed up on render.
    base, amp = 168.0, 34.0
    step = (W - 80) / max(len(weekly), 1)
    pts = " ".join(
        f"{40 + i * step:.1f},{base - (v / peak) * amp:.1f}" for i, v in enumerate(weekly)
    )
    h = 208
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{title}. {total} contributions in the last year.">
  <rect width="{W}" height="{h}" rx="4" fill="{T['PAPER']}" stroke="{T['LINE']}" stroke-width="1"/>
  <rect width="{W}" height="3" fill="{T['BLUE']}"/>
  <text x="40" y="54" font-family="{MONO}" font-size="24" font-weight="700" fill="{T['INK']}">{title}</text>
  <text x="40" y="78" font-family="{MONO}" font-size="13" fill="{T['DIM']}">{subtitle}</text>
  <text x="40" y="124" font-family="{MONO}" font-size="34" font-weight="700" fill="{T['INK']}">{total}</text>
  <text x="{40 + 21 * len(str(total))}" y="124" font-family="{MONO}" font-size="12" fill="{T['DIM']}">contributions in the last year</text>
  <text x="{W - 40}" y="124" font-family="{MONO}" font-size="12" fill="{T['DIM']}" text-anchor="end">{st.get('active_days', 0)} active days  ·  best week {st.get('best_week', 0)}</text>
  <polyline points="{pts}" fill="none" stroke="{T['BLUE']}" stroke-width="1.6" opacity="0.95"/>
  <line x1="40" y1="{base:.0f}" x2="{W - 40}" y2="{base:.0f}" stroke="{T['LINE']}" stroke-width="1"/>
</svg>
"""


def section(label: str) -> str:
    """A section rule, the way a CLI delimits its own output."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="26" viewBox="0 0 {W} 26" role="img" aria-label="{label}">
  <text x="0" y="17" font-family="{MONO}" font-size="12" font-weight="700" fill="{T['BLUE']}">{label}</text>
  <line x1="{len(label) * 7.4 + 14}" y1="12" x2="{W}" y2="12" stroke="{T['LINE']}" stroke-width="1"/>
</svg>
"""


def _tiers(grid):
    """Thresholds taken from the days that actually have contributions.

    A fixed scale either flattens a quiet year into one tier or blows a busy
    one out to solid @. Quantiles adapt to whatever the year was.
    """
    active = sorted(v for col in grid for v in col if v > 0)
    if not active:
        return [1, 2, 3]
    return [active[int(len(active) * f)] for f in (0.3, 0.6, 0.85)]


def calendar_ascii() -> str:
    """A year of daily contributions as characters on a five-step ramp."""
    st = _load("stats.json", {})
    grid = st.get("grid", [])
    months = st.get("months", [])
    if not grid:
        return section("stats")

    q = _tiers(grid)
    ramp = T["RAMP"]
    glyph = ["·", ":", "+", "#", "@"]

    def tier(v: int) -> int:
        if v == 0:
            return 0
        if v <= q[0]:
            return 1
        if v <= q[1]:
            return 2
        if v <= q[2]:
            return 3
        return 4

    cw, rh = 14.2, 15.0
    left, top = 62, 78

    rows = []
    for r, label in enumerate(("mon", "", "wed", "", "fri", "", "")):
        y = top + r * rh
        if label:
            rows.append(
                f'<text x="24" y="{y}" font-family="{MONO}" font-size="11" fill="{T["DIM"]}">{label}</text>'
            )
        # One tspan per run of equal intensity rather than per day: 371
        # elements would be a large file for something that never animates.
        spans, run_t, run_n = [], None, 0
        for col in grid:
            t = tier(col[r] if r < len(col) else 0)
            if t == run_t:
                run_n += 1
            else:
                if run_t is not None:
                    spans.append((run_t, run_n))
                run_t, run_n = t, 1
        if run_t is not None:
            spans.append((run_t, run_n))

        inner = "".join(f'<tspan fill="{ramp[t]}">{glyph[t] * n}</tspan>' for t, n in spans)
        rows.append(
            f'<text x="{left}" y="{y}" font-family="{MONO}" font-size="12.5" '
            f'letter-spacing="{cw - 7.6:.1f}" xml:space="preserve">{inner}</text>'
        )

    # Skip a label that would land on the previous one. The first week of the
    # range is usually partial, so month one and month two can be three days
    # apart and render as "juaug".
    placed, keep = -99, []
    for i, name in months:
        if i - placed < 3:
            continue
        placed = i
        keep.append((i, name))
    mlabels = "".join(
        f'<text x="{left + i * cw:.0f}" y="{top - 20}" font-family="{MONO}" font-size="10" fill="{T["DIM"]}">{name}</text>'
        for i, name in keep
    )

    height = top + 7 * rh + 40
    ly = height - 16
    gx = 62
    legend = "".join(
        f'<text x="{gx + i * 15}" y="{ly}" font-family="{MONO}" font-size="12" fill="{ramp[i]}">{glyph[i]}</text>'
        for i in range(5)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="A year of daily contributions. {st.get('total', 0)} total across {st.get('active_days', 0)} active days.">
  <rect width="{W}" height="{height}" rx="4" fill="{T['CARD']}" stroke="{T['LINE']}" stroke-width="1"/>
  <text x="24" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{T['DIM']}">THE YEAR</text>
  <text x="{W - 24}" y="34" font-family="{MONO}" font-size="11" fill="{T['DIM']}" text-anchor="end">{st.get('active_days', 0)} of 365 days had a contribution</text>
  <line x1="20" y1="48" x2="{W - 20}" y2="48" stroke="{T['LINE']}" stroke-width="1"/>
  {mlabels}
  {"".join(rows)}
  <text x="24" y="{ly}" font-family="{MONO}" font-size="10.5" fill="{T['DIM']}">less</text>
  {legend}
  <text x="{gx + 5 * 15 + 6}" y="{ly}" font-family="{MONO}" font-size="10.5" fill="{T['DIM']}">more</text>
</svg>
"""


def stats_panel() -> str:
    """Languages by bytes written, and the shape of the year."""
    langs = _load("languages.json", {})
    total_bytes = sum(langs.values()) or 1
    st = _load("stats.json", {})

    body, y = [], 78
    for name, val in list(langs.items())[:6]:
        pct = 100 * val / total_bytes
        body.append(
            f'<text x="24" y="{y}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}">{name.lower()}</text>'
            f'<rect x="150" y="{y - 9}" width="{int(pct / 100 * 300)}" height="8" fill="{T["BLUE"]}" opacity="0.9" rx="1"/>'
            f'<text x="470" y="{y}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}" text-anchor="end">{pct:.0f}%</text>'
        )
        y += 24

    ry = 78
    for label, val in (
        ("current streak", f"{st.get('current_streak', 0)} days"),
        ("longest streak", f"{st.get('longest_streak', 0)} days"),
        ("active days", f"{st.get('active_days', 0)} / 365"),
        ("public repos", str(st.get("public_repos", 0))),
    ):
        body.append(
            f'<text x="530" y="{ry}" font-family="{MONO}" font-size="12" fill="{T["DIM"]}">{label}</text>'
            f'<text x="{W - 24}" y="{ry}" font-family="{MONO}" font-size="12" font-weight="700" fill="{T["INK"]}" text-anchor="end">{val}</text>'
        )
        ry += 24

    height = max(y, ry) + 16
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Languages by bytes written">
  <rect width="{W}" height="{height}" rx="4" fill="{T['CARD']}" stroke="{T['LINE']}" stroke-width="1"/>
  <text x="24" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{T['DIM']}">BY BYTES WRITTEN</text>
  <text x="530" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{T['DIM']}">THE YEAR</text>
  <line x1="20" y1="48" x2="{W - 20}" y2="48" stroke="{T['LINE']}" stroke-width="1"/>
  {"".join(body)}
</svg>
"""


def main() -> None:
    global T
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, palette in THEMES.items():
        T = palette
        sfx = f"-{theme}"
        (OUT / f"header{sfx}.svg").write_text(
            banner("harshavardhan beesabathina", "systems and agent infrastructure · tirupati, india")
        )
        (OUT / f"header-antharmaya{sfx}.svg").write_text(
            banner("antharmaya labs", "agent and systems infrastructure · india")
        )
        for name in ("about", "stack", "projects", "stats"):
            (OUT / f"s-{name}{sfx}.svg").write_text(section(name))
        (OUT / f"stats{sfx}.svg").write_text(stats_panel())
        (OUT / f"calendar{sfx}.svg").write_text(calendar_ascii())
    print(f"wrote {len(list(OUT.glob('*.svg')))} svg files (light + dark)")


if __name__ == "__main__":
    main()
