#!/usr/bin/env python3
"""README visuals for dsh-github-bot: hero banners + the trust-boundary figure.

Everything below is derived from this repository's runtime, not from the README
prose:

  * ``src/approval-gate.ts`` registers one ``tools/pre-execute`` waterfall
    listener. It maps eight write tools to eight ``allowedActions`` entries
    (``pr.create``, ``pr.update``, ``pr.merge``, ``review.post``, ``issue.create``,
    ``issue.comment``, ``issue.close``, ``ci.run``): an action outside the
    whitelist is denied *before* any prompt, the CI driver
    (``DSH_GITHUB_CI_DRIVER=1`` + ``ci.autoApprove``) is allowed through the
    official policy seam, and everything else returns ``ask`` so the registry
    asks the human through ``ctx.approval`` (``approval/asked`` +
    ``approval/decided``). With no answerer it fails closed. Every other tool
    leaves through ``next()`` — that is the waterfall contract.
  * ``src/tools.ts`` registers fourteen model tools plus the one-shot
    ``ci_run`` when ``ci.enabled``: seven read tools (``gh_review``,
    ``gh_issue``, ``gh_search``, ``gh_repo``, ``gh_file``, ``gh_repo_search``,
    ``gh_checks``) that never touch the gate, and the eight writes above.
  * ``src/commands.ts`` registers four command families (``/pr create``,
    ``/review``, ``/issue open``, ``/ci``). Commands run with no open turn, so
    they never write: they gather read-only context and queue a model
    instruction; the model performs the write in its own turn, through the gate.
  * ``src/jobs.ts`` starts the ``github-review`` job on ``ctx.jobs`` (owner is
    the bare ``SessionId``), which fetches PR metadata + the capped diff,
    runs the deterministic analyzer of ``src/review.ts`` and keeps the report
    in process memory; the model reads it back with ``job_output`` and posts
    with the gated ``review_post``. The job itself never writes.
  * ``src/credential.ts`` resolves the token per operation (credentials seam →
    environment → ``gh`` CLI) and hands it only to the REST client; it never
    reaches results, events, rendering, jobs or errors.
  * ``src/ci/pipeline.ts`` runs the composite-action pass: metadata → label/path
    filters → idempotency → capped diff → analyzers → inline comments →
    status check → ``dsh-github-bot-ci-result.json`` / ``-summary.md``.

Figure one (hero, ``docs/assets/dsh-github-bot-hero-{zh,en}-{light,dark}.webp``,
1440x576) is the **gated PR lifecycle**: the four write stages of a pull
request (create → review → update → merge), each with its tool and action code,
each stamped by a human, with the background review job folded into the review
stage and the token/retry rail underneath. It is deliberately *not* the
boundary lanes — that is figure two.

Figure two (``docs/assets/dsh-github-bot-flow-v5-{light,dark}.svg``, 1100x660)
is the **two-sided trust boundary**: a vertical seam with the approval gate
mounted in it, a read lane that crosses the seam without stopping, a write lane
that stops at the gate, the background-job return path coming back up through
the gate, and the CI lane running underneath. Not a row of five boxes.

Fonts: Microsoft YaHei (msyh.ttc / msyhbd.ttc) for CJK, Consolas for mono,
Segoe UI for the Latin copy.

Run:  python scripts/gen-readme-assets.py
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
FONT_EN = r"C:\Windows\Fonts\segoeui.ttf"
FONT_EN_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD,
           FONT_EN, FONT_EN_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

KIND = {
    "cjk": FONT_CJK,
    "cjk_bold": FONT_CJK_BOLD,
    "mono": FONT_MONO,
    "mono_bold": FONT_MONO_BOLD,
    "en": FONT_EN,
    "en_bold": FONT_EN_BOLD,
}

# Family palette: accent #4B67B4 (dark #8496f5); page gradients #f9f6fd→#e4eaf8
# and #131a2a→#0c1016; radius 18–22; soft shadows.
SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e5e0f2",
        text="#17151f", sub="#4c5160", faint="#8a8fa2",
        accent="#4B67B4", pill="#ece7f9", grid="#ece8f5",
        ask="#a3681a", ask_bg="#fbf1e2",
        deny="#ad3a4e", ok="#24785f",
        shadow=(38, 30, 68),
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2d364a",
        text="#eef2fa", sub="#a8b1c4", faint="#737d92",
        accent="#8496f5", pill="#242d42", grid="#242c3d",
        ask="#e2ae57", ask_bg="#2a2636",
        deny="#f08a9c", ok="#6fd3ac",
        shadow=(0, 0, 0),
    ),
}

FAMILY = "#4B67B4"


# ── small colour / font helpers ─────────────────────────────────────────────

def font(size: float, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(KIND[kind], int(size))


def hx(value) -> tuple:
    if isinstance(value, tuple):
        return value[:3]
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def blend(a, b, t: float):
    """Paint colour a over base b at t (t = how much of a survives)."""
    pa, pb = hx(a), hx(b)
    return tuple(int(y * (1 - t) + x * t) for x, y in zip(pa, pb))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.34 * (y / h) + 0.66 * (y / h) ** 1.55
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return img


def glow(img: Image.Image, cx: int, cy: int, r: int, color, alpha: int):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(12, 0, -1):
        rr = r * i / 12
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 13)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def soft_card(img: Image.Image, box, skin, radius=20, lift=11, strength=1.0,
              outline=None, width=2) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x0 + 1, y0 + lift, x1 + 1, y1 + lift + 3],
                         radius=radius,
                         fill=hx(skin["shadow"]) + (int(34 * strength),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(skin["card"]),
                        outline=hx(outline or skin["card_edge"]), width=width)
    return base.convert("RGB")


def fit(d: ImageDraw.ImageDraw, text: str, maxw: float, start: int,
        kind: str, floor: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > floor:
        f = font(size, kind)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 1
    return font(floor, kind)


def tint(skin, color, t: float) -> tuple:
    return blend(color, skin["card"], t)


# ── hero: the gated PR lifecycle ────────────────────────────────────────────

HERO = {
    "zh": dict(
        kicker="DeepSeek Harness · GitHub 集成插件",
        eyebrow="dsh-github-bot",
        title="先批后写",
        value=["读直连；写过闸，没人批就拒绝。",
               "token 逐操作解析，永不进日志。"],
        sub="15 个工具 · 4 族命令 · 后台审查 job · CI 复合动作",
        meta="reviewMode: static · 8 个写动作逐条审批",
        foot="Apache-2.0 · github.com/PerryLink/dsh-github-bot",
        gate_label="tools/pre-execute · waterfall listener (next())",
        gate_title="每次写调用都停在这道闸",
        gate_note="allowedActions → 名单外直接拒绝",
        col_life="生命周期",
        col_tool="写工具 · 动作",
        col_route="REST 路由",
        col_gate="人工审批",
        rows=[
            ("创建", "pr_create", "pr.create", "POST /pulls"),
            ("审查", "review_post", "review.post", "POST /pulls/{n}/reviews"),
            ("更新", "pr_update", "pr.update", "PATCH /pulls/{n}"),
            ("合并", "pr_merge", "pr.merge", "PUT /pulls/{n}/merge"),
        ],
        review_sub="ctx.jobs · 静态分析器 · job_output",
        stamp="ASK · 人工",
        ask_note="没有应答者就拒绝 · 每次写留 approval/asked + approval/decided",
        rail="token: credentials → env → gh · 只进 Authorization 头",
        rail_right="429 → Retry-After",
    ),
    "en": dict(
        kicker="DeepSeek Harness · GitHub plugin",
        eyebrow="dsh-github-bot",
        title="Ask first.",
        value=["Reads pass; writes wait for a human.",
               "Fail closed. Token never logged."],
        sub="15 tools · 4 commands · review jobs · CI action",
        meta="reviewMode: static · 8 gated writes",
        foot="Apache-2.0 · github.com/PerryLink/dsh-github-bot",
        gate_label="tools/pre-execute · waterfall listener (next())",
        gate_title="every write stops at this gate",
        gate_note="allowedActions → deny before the prompt",
        col_life="lifecycle",
        col_tool="write tool · action",
        col_route="REST route",
        col_gate="human approval",
        rows=[
            ("create", "pr_create", "pr.create", "POST /pulls"),
            ("review", "review_post", "review.post", "POST /pulls/{n}/reviews"),
            ("update", "pr_update", "pr.update", "PATCH /pulls/{n}"),
            ("merge", "pr_merge", "pr.merge", "PUT /pulls/{n}/merge"),
        ],
        review_sub="ctx.jobs · static analyzer · job_output",
        stamp="ASK · human",
        ask_note="no answerer → the write is refused · every call logs asked → decided",
        rail="token: credentials → env → gh · only the Authorization header",
        rail_right="429 → Retry-After",
    ),
}

W, H = 1440, 576
COL_X, COL_W = 72, 500

# right zone geometry
RZ_X0, RZ_X1 = 612, 1368
ROWS = ((146, 62), (216, 96), (320, 62), (390, 62))
SPINE_X = 626
CARD_X0, CARD_X1 = 648, 1150
STAMP_X0, STAMP_X1 = 1170, 1350


def stamp(img: Image.Image, box, text: str, f, color, edge, angle: float):
    """A slightly rotated rubber stamp."""
    w = box[2] - box[0]
    h = box[3] - box[1]
    lay = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([12, 12, 12 + w, 12 + h], radius=10,
                        fill=hx(edge) + (46,), outline=hx(color) + (255,),
                        width=2)
    d.rounded_rectangle([17, 17, 7 + w, 7 + h], radius=7,
                        outline=hx(color) + (110,), width=1)
    d.text((12 + w / 2, 12 + h / 2 + 1), text, font=f, fill=hx(color),
           anchor="mm")
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    img.paste(lay, (box[0] - 12, box[1] - 12), lay)


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    Hd = HERO[lang]
    zh = lang == "zh"
    light = skin == "light"

    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1234, 44, 430, hx(s["accent"]), 24 if light else 46)
    img = glow(img, 210, 588, 320, hx(s["accent"]), 8 if light else 14)
    d = ImageDraw.Draw(img)

    # faint rule between the copy column and the lifecycle board
    d.line([(588, 60), (588, 520)], fill=hx(s["grid"]), width=2)

    # ── left column ────────────────────────────────────────────────────────
    fk = font(18, "cjk_bold" if zh else "en_bold")
    kw = d.textlength(Hd["kicker"], font=fk)
    pill_x, pill_y, pill_h = COL_X, 58, 38
    assert pill_x + kw + 44 <= COL_X + COL_W, "kicker overflows"
    d.rounded_rectangle([pill_x, pill_y, pill_x + kw + 44, pill_y + pill_h],
                        radius=pill_h // 2, fill=hx(s["pill"]))
    # the pill's leading mark: a closed latch
    d.arc([pill_x + 13, pill_y + 11, pill_x + 33, pill_y + 27], 200, 340,
          fill=hx(s["accent"]), width=3)
    d.rounded_rectangle([pill_x + 16, pill_y + 17, pill_x + 30, pill_y + 27],
                        radius=3, fill=hx(s["accent"]))
    d.text((pill_x + 40, pill_y + 8), Hd["kicker"], font=fk,
           fill=hx(s["accent"]))

    d.text((COL_X, 112), Hd["eyebrow"], font=font(26, "mono"),
           fill=hx(s["accent"]))

    f_title = fit(d, Hd["title"], COL_W, 84,
                  "cjk_bold" if zh else "en_bold", floor=80)
    assert f_title.size >= 80, (lang, f_title.size)
    d.text((COL_X, 152), Hd["title"], font=f_title, fill=hx(s["text"]))

    y = 268
    for line in Hd["value"]:
        f_v = fit(d, line, COL_W, 30, "cjk_bold" if zh else "en_bold", floor=26)
        assert d.textlength(line, font=f_v) <= COL_W, line
        d.text((COL_X, y), line, font=f_v, fill=hx(s["text"]))
        y += 40

    f_sub = fit(d, Hd["sub"], COL_W, 24, "cjk" if zh else "en", floor=22)
    assert d.textlength(Hd["sub"], font=f_sub) <= COL_W, Hd["sub"]
    d.text((COL_X, 362), Hd["sub"], font=f_sub, fill=hx(s["sub"]))

    f_meta = fit(d, Hd["meta"], COL_W, 19, "cjk" if zh else "en", floor=18)
    assert d.textlength(Hd["meta"], font=f_meta) <= COL_W, Hd["meta"]
    d.text((COL_X, 404), Hd["meta"], font=f_meta, fill=hx(s["faint"]))
    d.line([COL_X, 446, COL_X + COL_W, 446], fill=hx(s["grid"]), width=2)

    f_foot = font(16, "mono")
    assert d.textlength(Hd["foot"], font=f_foot) <= COL_W, "footer overflows"
    d.text((COL_X, 458), Hd["foot"], font=f_foot, fill=hx(s["faint"]))

    # ── right: the gate strip ──────────────────────────────────────────────
    img = soft_card(img, (RZ_X0, 36, RZ_X1, 108), s, radius=20, lift=9,
                    strength=0.85, outline=tint(s, s["ask"], 0.34))
    d = ImageDraw.Draw(img)
    f_gl = fit(d, Hd["gate_label"], 400, 12.5, "mono", floor=11)
    d.text((RZ_X0 + 24, 52), Hd["gate_label"], font=f_gl, fill=hx(s["ask"]))
    f_gt = fit(d, Hd["gate_title"], 430, 18,
               "cjk_bold" if zh else "en_bold", floor=16)
    d.text((RZ_X0 + 22, 74), Hd["gate_title"], font=f_gt, fill=hx(s["text"]))
    f_gn = fit(d, Hd["gate_note"], 300, 12, "cjk" if zh else "en", floor=11)
    assert d.textlength(Hd["gate_note"], font=f_gn) <= 300
    d.text((RZ_X1 - 24, 78), Hd["gate_note"], font=f_gn, fill=hx(s["faint"]),
           anchor="ra")

    # column headers
    for cx, label, anchor in ((CARD_X0 + 20, Hd["col_life"], "la"),
                              (CARD_X0 + 186, Hd["col_tool"], "la"),
                              (CARD_X1 - 20, Hd["col_route"], "ra"),
                              ((STAMP_X0 + STAMP_X1) / 2, Hd["col_gate"], "ma")):
        d.text((cx, 136), label, font=font(11, "cjk" if zh else "en"),
               fill=hx(s["sub"]), anchor=anchor)

    # spine behind the stage cards
    d.line([(SPINE_X, ROWS[0][0]), (SPINE_X, sum(ROWS[-1]) - 2)],
           fill=tint(s, s["accent"], 0.35), width=2)

    stamp_f = font(13, "cjk_bold" if zh else "en_bold")
    for index, ((top, height), row) in enumerate(zip(ROWS, Hd["rows"])):
        stage, tool, action, route = row
        cy = top + height / 2
        # spine dot
        d.ellipse([SPINE_X - 5, cy - 5, SPINE_X + 5, cy + 5],
                  fill=hx(s["accent"]))
        img = soft_card(img, (CARD_X0, top, CARD_X1, top + height), s,
                        radius=18, lift=8, strength=0.8,
                        outline=tint(s, s["ask"], 0.30))
        d = ImageDraw.Draw(img)
        # the review row is taller and carries the background job folded in
        nudge = -12 if index == 1 else 0
        f_stage = font(17, "cjk_bold" if zh else "en_bold")
        d.text((CARD_X0 + 20, cy - 12 + nudge), stage, font=f_stage,
               fill=hx(s["text"]))
        f_tool = fit(d, tool, 240, 13.5, "mono", floor=12)
        d.text((CARD_X0 + 186, cy - 13 + nudge), tool, font=f_tool,
               fill=hx(s["text"]))
        f_act = fit(d, action, 240, 11.5, "mono", floor=10.5)
        d.text((CARD_X0 + 186, cy + 7 + nudge), action, font=f_act,
               fill=hx(s["sub"]))
        f_route = fit(d, route, 210, 11.5, "mono", floor=10.5)
        d.text((CARD_X1 - 20, cy - 2), route, font=f_route,
               fill=hx(s["faint"]), anchor="ra")

        if index == 1:
            d.rounded_rectangle(
                [CARD_X0 + 20, cy + 10, CARD_X1 - 20, cy + 36], radius=9,
                fill=tint(s, s["accent"], 0.07),
                outline=tint(s, s["accent"], 0.26), width=1)
            f_sub = fit(d, Hd["review_sub"], CARD_X1 - CARD_X0 - 60, 11.5,
                        "cjk" if zh else "mono", floor=11)
            d.text((CARD_X0 + 32, cy + 16), Hd["review_sub"], font=f_sub,
                   fill=hx(s["accent"]))

        stamp(img, (STAMP_X0, int(cy) - 20, STAMP_X1, int(cy) + 20),
              Hd["stamp"], stamp_f, s["ask"], s["ask_bg"], -5)

    f_ask = fit(d, Hd["ask_note"], CARD_X1 - CARD_X0, 11.5,
                "cjk" if zh else "en", floor=11)
    assert d.textlength(Hd["ask_note"], font=f_ask) <= CARD_X1 - CARD_X0 + 60
    d.text((CARD_X0 + 2, 470), Hd["ask_note"], font=f_ask, fill=hx(s["faint"]))

    # ── right: token / retry rail ──────────────────────────────────────────
    d.line([(RZ_X0, 492), (RZ_X1, 492)], fill=hx(s["grid"]), width=2)
    f_rail = fit(d, Hd["rail"], 520, 12, "mono" if not zh else "cjk",
                 floor=11)
    d.text((RZ_X0, 508), Hd["rail"], font=f_rail, fill=hx(s["accent"]))
    d.text((RZ_X1, 508), Hd["rail_right"], font=font(11.5, "mono"),
           fill=hx(s["faint"]), anchor="ra")

    path = os.path.join(OUT, f"dsh-github-bot-hero-{lang}-{skin}.webp")
    img.save(path, "WEBP", quality=92, method=6)
    print(f"wrote {os.path.relpath(path, ROOT)}")


# ── flow (hand-written SVG): the two-sided trust boundary ───────────────────

SANS = "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"
MONO = "Consolas, SFMono-Regular, Menlo, monospace"


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    Wd, Ht = 1100, 660
    light = skin == "light"
    shadow_op = "0.13" if light else "0.48"
    e: list[str] = []

    def add(x: str) -> None:
        e.append(x)

    def tinthex(c, t):
        return "#%02x%02x%02x" % blend(c, s["card"], t)

    def txt(x, y, body, size=15, color=None, weight="400", mono=False,
            anchor="start", spacing=None):
        fam = MONO if mono else SANS
        extra = f' letter-spacing="{spacing}"' if spacing else ""
        add(f'<text x="{x}" y="{y}" fill="{color or s["text"]}" '
            f'font-family="{fam}" font-size="{size}" font-weight="{weight}"'
            f'{extra} text-anchor="{anchor}">{escape(body)}</text>')

    def rect(x, y, w, h, r=16, fill=None, stroke=None, sw=1.5, shadow=False):
        g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
             f'fill="{fill or s["card"]}"')
        if stroke:
            g += f' stroke="{stroke}" stroke-width="{sw}"'
        g += "/>"
        add(f'<g filter="url(#soft)">{g}</g>' if shadow else g)

    def line(x1, y1, x2, y2, stroke, w=2, dash=None, marker=None):
        g = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
             f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"')
        if dash:
            g += f' stroke-dasharray="{dash}"'
        if marker:
            g += f' marker-end="url(#{marker})"'
        add(g + "/>")

    def path(d, stroke, w=2, marker=None, dash=None):
        g = (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" '
             f'stroke-linecap="round" stroke-linejoin="round"')
        if dash:
            g += f' stroke-dasharray="{dash}"'
        if marker:
            g += f' marker-end="url(#{marker})"'
        add(g + "/>")

    ask, deny, accent = s["ask"], s["deny"], s["accent"]
    mono_c = tinthex(s["text"], 0.88)

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" '
        f'height="{Ht}" viewBox="0 0 {Wd} {Ht}" role="img" '
        f'aria-labelledby="fig-title">')
    add('<title id="fig-title">dsh-github-bot — the trust boundary: seven read '
        'tools cross the seam directly to api.github.com; the eight write tools '
        'stop at the tools/pre-execute gate, where allowedActions denies '
        'unknown actions before the prompt, the CI driver is allowed through '
        'ci.autoApprove, and everything else asks ctx.approval and fails '
        'closed without an answerer; the background review job returns through '
        'the same gate to post; the CI lane runs underneath; the token only '
        'ever travels in the Authorization header</title>')
    add("<defs>")
    add('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    add(f'<filter id="soft" x="-30%" y="-30%" width="170%" height="185%">'
        f'<feDropShadow dx="0" dy="7" stdDeviation="10" flood-color="#1b1735" '
        f'flood-opacity="{shadow_op}"/></filter>')
    for name, color in (("arr", accent), ("arra", ask), ("arrf", s["faint"])):
        add(f'<marker id="{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0.5 0.5 L9.5 5 L0.5 9.5 z" fill="{color}"/></marker>')
    add("</defs>")
    add(f'<rect width="{Wd}" height="{Ht}" rx="22" fill="url(#bg)"/>')
    add(f'<circle cx="1010" cy="66" r="210" fill="{accent}" '
        f'opacity="{0.05 if light else 0.10}"/>')

    # ── header ────────────────────────────────────────────────────────────
    txt(44, 50, "dsh-github-bot · the trust boundary", 23, s["text"], "700")
    txt(44, 78, "reads cross the seam directly; every write stops for a human",
        15, s["sub"])
    txt(1056, 50, "src/approval-gate.ts · registerApprovalGate()", 14,
        s["faint"], mono=True, anchor="end")
    txt(1056, 78, "8 gated writes · 7 direct reads · 4 command families", 13,
        accent, mono=True, anchor="end")
    line(44, 100, 1056, 100, s["grid"], 1.5)

    # ── the seam: a vertical wall with the gate mounted in it ──────────────
    add(f'<rect x="528" y="112" width="44" height="336" rx="14" '
        f'fill="{accent}" opacity="{0.09 if light else 0.16}"/>')
    line(536, 118, 536, 446, tinthex(accent, 0.72), 1.4)
    line(564, 118, 564, 446, tinthex(accent, 0.72), 1.4)
    line(550, 118, 550, 446, tinthex(accent, 0.4), 1.2, dash="3 7")
    add(f'<text x="550" y="182" fill="{s["sub"]}" font-family="{MONO}" '
        f'font-size="11" letter-spacing="2.4" text-anchor="middle" '
        f'transform="rotate(-90 550 182)">TRUST BOUNDARY</text>')

    # ── left: agent side ──────────────────────────────────────────────────
    # commands
    rect(44, 116, 376, 96, 18, s["card"], s["card_edge"], 1.5, shadow=True)
    txt(64, 142, "human commands · 4 families", 15, s["text"], "700")
    txt(400, 143, "never write", 11, s["faint"], anchor="end")
    txt(64, 166, "/pr create · /review · /issue open · /ci", 12, mono_c,
        mono=True)
    txt(64, 190, "gather read-only context, then queue a turn", 11, s["sub"])
    txt(64, 206, "the model writes in its own turn, through the gate", 11,
        s["faint"])

    # reads
    rect(44, 226, 376, 76, 18, s["card"], s["card_edge"], 1.5, shadow=True)
    txt(64, 252, "read tools · 7 · direct", 15, s["text"], "700")
    txt(400, 253, "ungated", 11, accent, anchor="end")
    txt(64, 276, "gh_review · gh_issue · gh_search · gh_repo", 12, mono_c,
        mono=True)
    txt(64, 295, "gh_file · gh_repo_search · gh_checks", 12, mono_c,
        mono=True)

    # writes
    rect(44, 316, 376, 132, 18, s["card"], tinthex(ask, 0.5), 1.7,
         shadow=True)
    txt(64, 342, "write tools · 8 · gated", 15, s["text"], "700")
    txt(400, 343, "ask", 11, ask, anchor="end")
    txt(64, 366, "pr_create · pr_update · pr_merge", 12, mono_c, mono=True)
    txt(64, 385, "review_post · issue_open · issue_comment", 12, mono_c,
        mono=True)
    txt(64, 404, "issue_close · ci_run", 12, mono_c, mono=True)
    txt(64, 432, "allowedActions decides before the prompt runs", 11, s["sub"])

    # ── the gate, mounted in the seam ─────────────────────────────────────
    rect(452, 316, 248, 132, 18, s["card"], ask, 2, shadow=True)
    txt(472, 342, "tools/pre-execute", 15, s["text"], "700")
    txt(680, 343, "gate", 11, ask, mono=True, anchor="end")
    txt(472, 368, "allowedActions → deny", 11.5, s["sub"], mono=True)
    txt(472, 386, "CI driver → allow", 11.5, s["sub"], mono=True)
    txt(472, 404, "else ask → ctx.approval", 11.5, s["text"], mono=True)
    txt(472, 422, "no answerer → fail closed", 11.5, s["sub"], mono=True)
    txt(472, 441, "approval/asked · approval/decided", 11, s["faint"])

    # read lane: straight across the seam, over the wall
    path("M420 264h300", accent, 2.4, marker="arr")
    txt(424, 254, "direct", 11, accent)
    txt(582, 254, "no approval", 11, s["sub"])

    # write lane: card → gate → GitHub
    path("M420 382h28", ask, 2.4, marker="arra")
    path("M700 382h32", ask, 2.4, marker="arra")

    # ── right: GitHub side ────────────────────────────────────────────────
    # token card
    rect(736, 116, 320, 96, 18, s["card"], s["card_edge"], 1.5, shadow=True)
    txt(756, 142, "token · per operation", 15, s["text"], "700")
    txt(1036, 143, "never logged", 11, s["faint"], anchor="end")
    txt(756, 166, "credentials → env → gh", 12, mono_c, mono=True)
    txt(756, 190, "only the Authorization header carries it", 11, s["sub"])
    txt(756, 206, "results, events and errors never see the value", 11,
        s["faint"])

    # reads land
    rect(736, 226, 320, 76, 18, s["card"], s["card_edge"], 1.5, shadow=True)
    txt(756, 252, "api.github.com · GET", 15, s["text"], "700")
    txt(756, 276, "429 → Retry-After · quota visible", 12, mono_c, mono=True)
    txt(756, 295, "the canonical value returns as tool/result", 11, s["sub"])

    # writes land
    rect(736, 316, 320, 132, 18, s["card"], tinthex(ask, 0.5), 1.7,
         shadow=True)
    txt(756, 342, "writes land here", 15, s["text"], "700")
    txt(1036, 343, "REST", 11, s["faint"], mono=True, anchor="end")
    txt(756, 366, "PR create · update · merge", 12, mono_c, mono=True)
    txt(756, 385, "review comments · summary | inline", 12, mono_c, mono=True)
    txt(756, 404, "issue open · comment · close", 12, mono_c, mono=True)
    txt(756, 430, "status check · success | needs-changes", 11, s["sub"],
        mono=True)

    # ── bottom: the job return path and the CI lane ───────────────────────
    # return path: the job report comes back up through the gate
    path("M480 474V452", ask, 2, marker="arra", dash="6 5")
    txt(490, 468, "review_post", 11, ask, mono=True)

    rect(44, 474, 456, 106, 18, s["card"], tinthex(accent, 0.42), 1.6,
         shadow=True)
    txt(64, 500, "background review job", 15, s["text"], "700")
    txt(480, 501, "ctx.jobs", 11, accent, mono=True, anchor="end")
    txt(64, 524, "/review <pr> → github-review → static analyzer", 12, mono_c,
        mono=True)
    txt(64, 543, "reviewMode: static | model · maxDiffChars 8000", 12, mono_c,
        mono=True)
    txt(64, 566, "report stays in memory · the job itself never writes", 11,
        s["sub"])

    rect(540, 474, 516, 106, 18, s["card"], s["card_edge"], 1.5, shadow=True)
    txt(560, 500, "CI lane · action.yml composite", 15, s["text"], "700")
    txt(1036, 501, "ci_run", 11, ask, mono=True, anchor="end")
    txt(560, 524, "dsh headless → label/path filters → capped diff", 12,
        mono_c, mono=True)
    txt(560, 543, "inline comments + status check → result.json / summary.md",
        11.5, mono_c, mono=True)
    txt(560, 566, "idempotent per head commit · ci.autoApprove is the allowlist",
        11, s["sub"])

    # ── footer rails ──────────────────────────────────────────────────────
    txt(44, 602, "token: credentials seam → env → gh, resolved per operation · "
        "only ever the Authorization header", 12, accent, mono=True)
    txt(44, 622, "429 → Retry-After / x-ratelimit-reset · requestTimeoutMs 30 s "
        "· remaining quota on every result", 11.5, s["sub"], mono=True)
    txt(44, 642, "the gate delegates every other tool through next() · "
        "Apache-2.0 · PerryLink DSH plugin family", 11, s["faint"])
    txt(1056, 642, "scripts/gen-readme-assets.py", 11, s["faint"], mono=True,
        anchor="end")

    add("</svg>")
    return "\n".join(e) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-github-bot-flow-v5-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote docs/assets/dsh-github-bot-flow-v5-{skin}.svg")


if __name__ == "__main__":
    main()
