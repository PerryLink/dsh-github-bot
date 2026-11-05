#!/usr/bin/env python3
"""Generate README image assets for dsh-github-bot (docs/assets/).

Outputs (idempotent overwrite):
  dsh-github-bot-flow-light.svg / dsh-github-bot-flow-dark.svg
      Hero workflow diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside is command-surface tokens only
      (pr_create, tools/pre-execute, ctx.approval, api.github.com, /review,
      /ci, config keys), so all five README languages share the same pair.

This plugin has no UI and no benchmark data, so there are no screenshots to
process and no evidence chart to draw. The older single-skin assets
(dsh-github-flow.svg, -hero.png, -demo.gif, -demo.png) are kept untouched for
external deep links; the READMEs reference only the new pair.

Run once:  python scripts/gen-readme-assets.py
Requires:  nothing beyond the standard library (the CJK probe below keeps
           parity with the family script so a localized bitmap later fails
           loudly instead of rendering tofu boxes).
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# --- CJK font probe: kept for parity with the family pipeline ----------------
# The SVGs below carry command tokens only (ASCII), so no CJK font is needed
# for them; the probe stays so that adding a localized bitmap later fails
# loudly instead of rendering tofu boxes.
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


# ---------------------------------------------------------------------------
# Hero workflow SVG (light + dark): write tool → approval gate → approval seam
# → GitHub REST → checks verdict, plus the /review job and /ci gate rails.
# All labels are command/config tokens, shared by five languages.
# ---------------------------------------------------------------------------
FLOW_NODES = [
    ("pr_create", "pr_merge · issue_open"),
    ("tools/pre-execute", "ask · deny"),
    ("ctx.approval", "approval/asked"),
    ("api.github.com", "429 → Retry-After"),
    ("gh_checks", "success | needs-changes"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 420
    nw, nh, gap = 180, 96, 45
    y0 = 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dsh-github-bot '
        f'workflow">',
        f'<title>dsh-github-bot workflow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-github-bot</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">pr_create · /review · /ci · 15 tools · '
        f'4 command families</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW_NODES):
        x = 60 + i * (nw + gap)
        accent = GREEN[skin] if i == len(FLOW_NODES) - 1 else (
            FAMILY if i == 1 else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 40}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="16" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 68}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # credential/allowlist bar under the gate + REST nodes
    bx, bw, by, bh = 285, 630, 282, 48
    for cx in (375, 825):  # node2 / node4 center-bottom connectors
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{by - y0 - nh}" '
            f'stroke="{FAMILY}" stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 31}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="13">tokenSource: auto · tokenRef: GITHUB_TOKEN · '
        f'allowedActions · maxRetries: 3</text>')
    parts.append(
        f'<text x="60" y="372" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">/review → ctx.jobs → reviewMode: static '
        f'→ review_post</text>')
    parts.append(
        f'<text x="60" y="398" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">/ci → action.yml → ci_run → '
        f'success | needs-changes</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(
                OUT, f"dsh-github-bot-flow-{skin}.svg"),
                "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/")


if __name__ == "__main__":
    main()
