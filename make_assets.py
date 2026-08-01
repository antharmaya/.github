#!/usr/bin/env python3
"""Generate every graphic on this profile.

Nothing here is embedded from a third-party server. Badge and stat-card
services rate-limit, go down, change their rendering, and see the traffic of
everyone who visits your profile. A profile that claims to care about
dependencies should not have ten of them above the fold.

So: plain SVG, written here, committed to the repo. GitHub serves it.

    python3 tools/make_assets.py

Fonts are the viewer's own monospace stack rather than a webfont, because
GitHub strips <style> blocks with @font-face from README SVGs anyway, and a
subsetted font is a large binary to carry for a heading.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# Deep ink and one ember accent. Legible against GitHub's light and dark
# themes alike, which is why the panel carries its own background instead of
# relying on the page.
VOID = "#0a0c11"
PANEL = "#0f131b"
LINE = "#1c2330"
DIM = "#67748a"
TEXT = "#c9d1dd"
BRIGHT = "#e8edf5"
EMBER = "#ff7a45"

MONO = (
    "ui-monospace,SFMono-Regular,'SF Mono','JetBrains Mono',"
    "Menlo,Consolas,'DejaVu Sans Mono',monospace"
)


def header(title: str, subtitle: str, width: int = 860, height: int = 150) -> str:
    """The banner. A stall ribbon, because that is what I actually work on."""
    # Deterministic block widths: a signal, not decoration, and identical on
    # every regeneration so the diff stays empty when nothing changed.
    widths = [58, 30, 76, 46, 24, 98, 38, 60, 84, 42, 66, 28]
    blocks, x = [], 300
    for i, w in enumerate(widths):
        if x + w > width - 40:
            break
        fill = EMBER if i % 3 else "#c4441f"
        op = "0.92" if i % 3 else "0.8"
        blocks.append(
            f'<rect x="{x}" y="104" width="{w}" height="22" fill="{fill}" opacity="{op}"/>'
        )
        x += w + 14

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title} — {subtitle}">
  <rect width="{width}" height="{height}" rx="4" fill="{VOID}"/>
  <rect width="{width}" height="3" fill="{EMBER}"/>
  <text x="34" y="52" font-family="{MONO}" font-size="26" font-weight="700" fill="{BRIGHT}">{title}</text>
  <text x="34" y="80" font-family="{MONO}" font-size="14" fill="{DIM}">{subtitle}</text>
  <text x="34" y="120" font-family="{MONO}" font-size="12" fill="{DIM}">io.pressure</text>
  {"".join(blocks)}
</svg>
"""


def section(label: str, width: int = 860) -> str:
    """A section rule, the way a CLI delimits its own output."""
    text_w = len(label) * 8.4 + 24
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="30" viewBox="0 0 {width} 30" role="img" aria-label="{label}">
  <text x="0" y="20" font-family="{MONO}" font-size="13" fill="{LINE}">──</text>
  <text x="26" y="20" font-family="{MONO}" font-size="13" font-weight="700" fill="{EMBER}">{label}</text>
  <line x1="{text_w + 8}" y1="15" x2="{width}" y2="15" stroke="{LINE}" stroke-width="1"/>
</svg>
"""


def shipped(rows, width: int = 860) -> str:
    """The numbers. Every one of these is checked before it is written here."""
    row_h, top = 34, 74
    height = top + row_h * len(rows) + 22
    body = []
    for i, (name, detail, where) in enumerate(rows):
        y = top + i * row_h
        if i:
            body.append(
                f'<line x1="20" y1="{y - 12}" x2="{width - 20}" y2="{y - 12}" stroke="{LINE}" stroke-width="1"/>'
            )
        body.append(
            f'<text x="24" y="{y + 8}" font-family="{MONO}" font-size="14" font-weight="700" fill="{BRIGHT}">{name}</text>'
            f'<text x="210" y="{y + 8}" font-family="{MONO}" font-size="13" fill="{TEXT}">{detail}</text>'
            f'<text x="{width - 24}" y="{y + 8}" font-family="{MONO}" font-size="12" fill="{EMBER}" text-anchor="end">{where}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Published work">
  <rect width="{width}" height="{height}" rx="4" fill="{PANEL}" stroke="{LINE}" stroke-width="1"/>
  <text x="24" y="34" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{DIM}">PUBLISHED, INSTALLABLE TODAY</text>
  <line x1="20" y1="50" x2="{width - 20}" y2="50" stroke="{LINE}" stroke-width="1"/>
  {"".join(body)}
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    (OUT / "header.svg").write_text(
        header("harshavardhan beesabathina", "systems and agent infrastructure  ·  tirupati, india")
    )
    (OUT / "header-antharmaya.svg").write_text(
        header("antharmaya labs", "agent and systems infrastructure  ·  india")
    )

    for name in ("about", "shipped", "stack", "how", "projects"):
        (OUT / f"s-{name}.svg").write_text(section(name))

    # Verified 2026-08-01 against crates.io, npm and PyPI, and by running the
    # suites. Re-check before changing a number here.
    (OUT / "shipped.svg").write_text(
        shipped(
            [
                ("stallwatch", "133 tests  ·  0 dependencies  ·  Rust", "crates.io"),
                ("rateguard", "783 test functions  ·  Go / Node / Python", "npm · pypi · go"),
                ("memory-bridge", "108 tests  ·  MCP server  ·  Python", "pypi"),
                ("systems-forge", "cross-agent operating contract  ·  MIT", "github"),
                ("horizon-os", "agent fleet control plane  ·  MIT", "github"),
                ("vectored", "WebGPU + Rust/WASM vectorizer", "live"),
            ]
        )
    )
    print(f"wrote {len(list(OUT.glob('*.svg')))} svg files to {OUT}")


if __name__ == "__main__":
    main()
