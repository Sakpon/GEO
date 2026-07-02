"""
Build the thedent.co.th SEO + GEO remediation deck.

Design system
-------------
- 16:9 widescreen (13.333" x 7.5")
- Primary:   #0E5C5C  (deep clinical teal — trust, calm, medical-without-corporate)
- Primary-2: #2A8C8C  (mid teal — bands, accents)
- Accent:    #E96A4D  (warm coral — alerts, CTAs, P0 markers)
- Accent-2:  #F5C26B  (warm sand — P1 markers)
- Ink:       #1A2331  (body text)
- Muted:     #5B6675  (captions, footers)
- Wash:      #F4F2EE  (background bands, table fills)
- Hairline:  #D9D5CE  (dividers)

Typography (Calibri — bundled with PowerPoint)
- Title:    36–48pt, weight bold, primary
- H1:       28pt, bold, primary
- H2:       18pt, semibold, ink
- Body:     14pt, ink
- Caption:  10pt, muted, italic

Spine
- Every content slide carries a hairline divider under the title,
  a left-aligned section label in the top-left, and a footer
  with "thedent.co.th — SEO & GEO Remediation  ·  2026-04-19  ·  N/M"
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# --- design tokens ---------------------------------------------------------
PRIMARY   = RGBColor(0x0E, 0x5C, 0x5C)
PRIMARY_2 = RGBColor(0x2A, 0x8C, 0x8C)
ACCENT    = RGBColor(0xE9, 0x6A, 0x4D)
ACCENT_2  = RGBColor(0xF5, 0xC2, 0x6B)
INK       = RGBColor(0x1A, 0x23, 0x31)
MUTED     = RGBColor(0x5B, 0x66, 0x75)
WASH      = RGBColor(0xF4, 0xF2, 0xEE)
HAIRLINE  = RGBColor(0xD9, 0xD5, 0xCE)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

OUT_PATH = Path("/home/user/GEO/workspace/plans/2026-04-19-remediation-deck.pptx")

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]


# --- helpers ---------------------------------------------------------------
def add_slide():
    return prs.slides.add_slide(BLANK)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def stroke_none(shape):
    shape.line.fill.background()


def rect(slide, x, y, w, h, color, line=False):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(s, color)
    if not line:
        stroke_none(s)
    return s


def line(slide, x1, y1, x2, y2, color=HAIRLINE, weight=0.75):
    ln = slide.shapes.add_connector(1, x1, y1, x2, y2)
    ln.line.color.rgb = color
    ln.line.width = Pt(weight)
    return ln


def text(slide, x, y, w, h, content, *, size=14, bold=False, color=INK,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
         font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = content if isinstance(content, list) else [content]
    for i, ln_ in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = ln_
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb


def bullets(slide, x, y, w, h, items, *, size=14, color=INK, bullet="•",
            spacing=4, font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(spacing)
        run = p.add_run()
        run.text = f"{bullet}  {item}"
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return tb


def slide_chrome(slide, section_label, page, total, *, title=None):
    # section label top-left
    text(slide, Inches(0.55), Inches(0.35), Inches(6), Inches(0.3),
         section_label.upper(), size=10, bold=True, color=PRIMARY_2)
    # title
    if title:
        text(slide, Inches(0.55), Inches(0.6), Inches(12), Inches(0.9),
             title, size=28, bold=True, color=PRIMARY)
        # hairline under title
        line(slide, Inches(0.55), Inches(1.45), Inches(12.78), Inches(1.45))
    # footer band
    rect(slide, Emu(0), Inches(7.18), SLIDE_W, Inches(0.32), WASH)
    text(slide, Inches(0.55), Inches(7.22), Inches(8), Inches(0.25),
         "thedent.co.th  ·  SEO & GEO Remediation  ·  2026-04-19",
         size=9, color=MUTED)
    text(slide, Inches(11), Inches(7.22), Inches(1.78), Inches(0.25),
         f"{page} / {total}", size=9, color=MUTED, align=PP_ALIGN.RIGHT)


TOTAL = 16
page = [0]
def step():
    page[0] += 1
    return page[0], TOTAL


# ==========================================================================
# 01 — Cover
# ==========================================================================
s = add_slide()
# Left color block
rect(s, Emu(0), Emu(0), Inches(4.6), SLIDE_H, PRIMARY)
# Right wash background
rect(s, Inches(4.6), Emu(0), SLIDE_W - Inches(4.6), SLIDE_H, WHITE)

# Accent vertical bar
rect(s, Inches(4.6), Emu(0), Inches(0.08), SLIDE_H, ACCENT)

# Brand mark on dark
text(s, Inches(0.6), Inches(0.55), Inches(4), Inches(0.4),
     "THE DENT  ·  BANGKOK", size=11, bold=True, color=WHITE)

# Eyebrow on light
text(s, Inches(5.1), Inches(1.4), Inches(7.6), Inches(0.4),
     "SEO & GEO AGENCY REPORT", size=11, bold=True, color=PRIMARY_2)

# Headline
text(s, Inches(5.1), Inches(1.85), Inches(7.8), Inches(2.6),
     ["thedent.co.th",
      "Remediation Report &",
      "90-Day Action Plan"],
     size=40, bold=True, color=PRIMARY)

# Sub
text(s, Inches(5.1), Inches(4.6), Inches(7.8), Inches(0.5),
     "Restoring crawlability and building durable SEO + AI-search visibility.",
     size=16, color=INK)

# Meta block
line(s, Inches(5.1), Inches(5.6), Inches(12.7), Inches(5.6))
text(s, Inches(5.1), Inches(5.75), Inches(7.6), Inches(0.3),
     "Prepared by   ·   SEO & GEO Agency (Agent Orchestra)",
     size=11, color=MUTED)
text(s, Inches(5.1), Inches(6.05), Inches(7.6), Inches(0.3),
     "Date              ·   2026-04-19",
     size=11, color=MUTED)
text(s, Inches(5.1), Inches(6.35), Inches(7.6), Inches(0.3),
     "Status           ·   Action required — site currently uncrawlable",
     size=11, color=ACCENT, bold=True)


# ==========================================================================
# 02 — Executive summary (big number alert)
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "01  ·  Executive summary", p, t,
             title="The site is currently invisible to search and AI engines.")

# Left: big number callout
rect(s, Inches(0.55), Inches(1.75), Inches(4.6), Inches(4.6), PRIMARY)
text(s, Inches(0.8), Inches(1.95), Inches(4.2), Inches(0.5),
     "HTTP STATUS RETURNED TO CRAWLERS", size=11, bold=True, color=ACCENT_2)
text(s, Inches(0.8), Inches(2.5), Inches(4.2), Inches(2.6),
     "403", size=180, bold=True, color=WHITE, font="Calibri")
text(s, Inches(0.8), Inches(5.2), Inches(4.2), Inches(0.5),
     "host_not_allowed", size=14, bold=True, color=ACCENT_2,
     font="Consolas")
text(s, Inches(0.8), Inches(5.6), Inches(4.2), Inches(0.7),
     "Homepage, www, robots.txt, sitemap.xml, and llms.txt all blocked at the edge.",
     size=12, color=WHITE)

# Right: what this means
text(s, Inches(5.6), Inches(1.75), Inches(7.2), Inches(0.4),
     "WHAT THIS MEANS", size=11, bold=True, color=PRIMARY_2)
bullets(s, Inches(5.6), Inches(2.15), Inches(7.4), Inches(3.2),
        ["Google cannot crawl or refresh the site — ranked pages will drop out of the index.",
         "ChatGPT, Perplexity, Google AI Overviews, Gemini, and Claude cannot read the site at query time — the clinic is excluded from AI answers.",
         "Every other on-page or content issue is invisible behind this block and cannot be diagnosed until crawlers can reach the site."],
        size=14, spacing=10)

# Bottom: the one urgent action
rect(s, Inches(5.6), Inches(5.5), Inches(7.4), Inches(1.3), WASH)
rect(s, Inches(5.6), Inches(5.5), Inches(0.12), Inches(1.3), ACCENT)
text(s, Inches(5.85), Inches(5.6), Inches(7.0), Inches(0.35),
     "MOST URGENT ACTION (TODAY)", size=10, bold=True, color=ACCENT)
text(s, Inches(5.85), Inches(5.95), Inches(7.0), Inches(0.85),
     ["Remove the host_not_allowed edge rule and verify",
      "curl -I https://thedent.co.th/  returns HTTP 200 for both a browser and a Googlebot user agent."],
     size=12, color=INK)


# ==========================================================================
# 03 — Two-stage framing
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "02  ·  Approach", p, t,
             title="A two-stage program: unblock, then build.")

# Two large cards
def card(slide, x, w, label, headline, body, color):
    rect(slide, x, Inches(1.95), w, Inches(4.6), WASH)
    rect(slide, x, Inches(1.95), w, Inches(0.7), color)
    text(slide, x + Inches(0.3), Inches(2.05), w - Inches(0.6), Inches(0.5),
         label, size=11, bold=True, color=WHITE)
    text(slide, x + Inches(0.3), Inches(2.35), w - Inches(0.6), Inches(0.4),
         headline, size=15, bold=True, color=WHITE)
    bullets(slide, x + Inches(0.3), Inches(2.95), w - Inches(0.6), Inches(3.4),
            body, size=13, spacing=8)

card(s, Inches(0.55), Inches(6.0), "STAGE 1  ·  EMERGENCY",
     "Restore crawlability (Days 0–7)",
     ["Remove edge block; site returns 200 to all crawlers",
      "Publish working robots.txt, sitemap.xml, and llms.txt",
      "Resubmit to Google Search Console and Bing",
      "Allowlist major AI-engine crawlers explicitly",
      "Capture a baseline crawl + AI-citation snapshot once reachable"],
     ACCENT)
card(s, Inches(6.78), Inches(6.0), "STAGE 2  ·  BUILD-OUT",
     "Foundations to citations (Weeks 2–13)",
     ["Phase 1 — technical SEO, schema, local + Core Web Vitals",
      "Phase 2 — E-E-A-T (doctor profiles, reviewer signals) + content",
      "Phase 3 — entity footprint, GEO scale, durable measurement",
      "Outcome — indexed, optimized, and reliably cited by AI engines"],
     PRIMARY)

text(s, Inches(0.55), Inches(6.7), Inches(12.3), Inches(0.4),
     "Every Phase 1–3 task assumes Stage 1 is complete. Without crawlability, the rest is unmeasurable.",
     size=12, italic=True, color=MUTED)


# ==========================================================================
# 04 — Current state — crawlability table
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "03  ·  Current state", p, t,
             title="Crawlability — every key URL is denied at the edge.")

# Simple custom table
def cell(slide, x, y, w, h, value, *, bg=WHITE, color=INK, bold=False,
         size=12, align=PP_ALIGN.LEFT, font="Calibri"):
    rect(slide, x, y, w, h, bg)
    tb = slide.shapes.add_textbox(x + Inches(0.12), y, w - Inches(0.24), h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_ = tf.paragraphs[0]
    p_.alignment = align
    run = p_.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


cols = [Inches(5.0), Inches(2.6), Inches(4.7)]
xs = [Inches(0.55)]
xs.append(xs[0] + cols[0])
xs.append(xs[1] + cols[1])

row_h = Inches(0.55)
y = Inches(1.85)

# header
cell(s, xs[0], y, cols[0], row_h, "Resource", bg=PRIMARY, color=WHITE, bold=True, size=12)
cell(s, xs[1], y, cols[1], row_h, "Status", bg=PRIMARY, color=WHITE, bold=True, size=12, align=PP_ALIGN.CENTER)
cell(s, xs[2], y, cols[2], row_h, "Impact", bg=PRIMARY, color=WHITE, bold=True, size=12)
y += row_h

rows = [
    ("https://thedent.co.th/",                "403 host_not_allowed", "Homepage uncrawlable"),
    ("https://www.thedent.co.th/",            "403 host_not_allowed", "www variant uncrawlable"),
    ("https://thedent.co.th/robots.txt",      "403",                  'Google treats as "unreachable" — crawl slows / stops if >30 days'),
    ("https://thedent.co.th/sitemap.xml",     "403",                  "No URL discovery aid"),
    ("https://thedent.co.th/llms.txt",        "403",                  "No AI-engine site map — likely doesn't exist yet"),
]
for i, (a, b, c) in enumerate(rows):
    bg = WASH if i % 2 == 0 else WHITE
    cell(s, xs[0], y, cols[0], row_h, a, bg=bg, size=11, font="Consolas")
    cell(s, xs[1], y, cols[1], row_h, b, bg=bg, size=11, bold=True, color=ACCENT, align=PP_ALIGN.CENTER, font="Consolas")
    cell(s, xs[2], y, cols[2], row_h, c, bg=bg, size=11)
    y += row_h

# Diagnosis callout
y += Inches(0.2)
rect(s, Inches(0.55), y, Inches(12.23), Inches(1.5), WASH)
rect(s, Inches(0.55), y, Inches(0.12), Inches(1.5), PRIMARY_2)
text(s, Inches(0.8), y + Inches(0.15), Inches(11.8), Inches(0.35),
     "DIAGNOSIS", size=10, bold=True, color=PRIMARY_2)
text(s, Inches(0.8), y + Inches(0.5), Inches(11.8), Inches(1.0),
     ["An origin / edge host-allowlist (CDN host rule, reverse-proxy server_name, or origin firewall) rejects general traffic before",
      "any application logic runs. The block is indiscriminate, not bot-specific. TLS/HTTP2 and DNS are healthy — recovery is near-instant once the rule is corrected."],
     size=12, color=INK)


# ==========================================================================
# 05 — Impact: SEO + GEO citation-extinction timeline
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "04  ·  Impact", p, t,
             title="Left unfixed, citation visibility decays to zero.")

# Left: SEO impact card
rect(s, Inches(0.55), Inches(1.85), Inches(5.6), Inches(5.0), WASH)
text(s, Inches(0.8), Inches(2.0), Inches(5.2), Inches(0.35),
     "SEO IMPACT", size=11, bold=True, color=PRIMARY)
text(s, Inches(0.8), Inches(2.35), Inches(5.2), Inches(0.5),
     "Indexation + measurement blocked", size=18, bold=True, color=INK)
bullets(s, Inches(0.8), Inches(3.0), Inches(5.2), Inches(3.8),
        ["Persistent 403s → deindexing of ranked pages",
         "New / updated pages will not be discovered",
         "PageSpeed, Lighthouse, and crawler audits cannot run against a 403",
         "Silent duration unknown — third-party allowlisted monitors may have missed it"],
        size=13, spacing=8)

# Right: GEO timeline
rect(s, Inches(6.4), Inches(1.85), Inches(6.4), Inches(5.0), PRIMARY)
text(s, Inches(6.65), Inches(2.0), Inches(6.0), Inches(0.35),
     "GEO  ·  CITATION-EXTINCTION TIMELINE", size=11, bold=True, color=ACCENT_2)

# 3 stops
def stop(slide, y, when, body):
    rect(slide, Inches(6.65), y, Inches(0.12), Inches(1.0), ACCENT)
    text(slide, Inches(6.85), y, Inches(5.7), Inches(0.35),
         when, size=11, bold=True, color=ACCENT_2)
    text(slide, Inches(6.85), y + Inches(0.35), Inches(5.7), Inches(0.7),
         body, size=12, color=WHITE)

stop(s, Inches(2.55), "T + 0–4 weeks",
     "Cached snapshots in Bing/Google/Common Crawl still surface; existing training data still references the site.")
stop(s, Inches(3.85), "T + 1–3 months",
     "Caches expire. Engines that re-verify before citing (Perplexity, ChatGPT browsing) silently drop the clinic.")
stop(s, Inches(5.15), "T + 6 months+",
     "Next-gen training corpora (fresh GPTBot/CCBot crawls) lack the site entirely. Open-crawl competitors take the citation slots.")


# ==========================================================================
# 06 — What's already healthy
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "05  ·  Current state", p, t,
             title="Foundations that are already healthy.")

def good_card(x, y, w, h, label, body):
    rect(s, x, y, w, h, WASH)
    rect(s, x, y, Inches(0.12), h, PRIMARY_2)
    text(s, x + Inches(0.3), y + Inches(0.25), w - Inches(0.5), Inches(0.4),
         label, size=14, bold=True, color=PRIMARY)
    text(s, x + Inches(0.3), y + Inches(0.7), w - Inches(0.5), h - Inches(0.8),
         body, size=12, color=INK)

cards_w = Inches(4.0)
cards_h = Inches(2.2)
gap = Inches(0.18)
top_y = Inches(1.95)
x0 = Inches(0.55)

good_card(x0,                              top_y, cards_w, cards_h,
          "HTTPS / HTTP-2",
          "Configured and negotiating cleanly. No protocol-level concerns.")
good_card(x0 + cards_w + gap,              top_y, cards_w, cards_h,
          "DNS",
          "Resolves to a single clean A record (210.246.201.242). No split-horizon issues.")
good_card(x0 + 2 * (cards_w + gap),        top_y, cards_w, cards_h,
          "Structured deny",
          "Fast, headered (x-deny-reason). Easy to diagnose, near-instant to undo.")

# Bottom callout
rect(s, x0, Inches(4.6), Inches(12.23), Inches(2.0), WASH)
text(s, Inches(0.8), Inches(4.8), Inches(11.6), Inches(0.5),
     "Implication", size=12, bold=True, color=PRIMARY_2)
text(s, Inches(0.8), Inches(5.15), Inches(11.6), Inches(1.4),
     ["Stage 1 recovery should be measured in hours, not weeks. The hard work is everything that comes after —",
      "rebuilding indexation, schema, local presence, E-E-A-T signals, and the entity footprint that drives AI citations."],
     size=14, color=INK)


# ==========================================================================
# 07 — 90-day plan overview (swim-lane timeline)
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "06  ·  Plan overview", p, t,
             title="The 90-day plan at a glance.")

# Timeline bar
tl_x = Inches(0.55)
tl_w = Inches(12.23)
tl_y = Inches(2.0)
tl_h = Inches(0.45)

rect(s, tl_x, tl_y, tl_w, tl_h, WASH)
# 13 week ticks
for i in range(14):
    px = tl_x + Emu(int(tl_w * (i / 13)))
    line(s, px, tl_y, px, tl_y + tl_h, color=HAIRLINE, weight=0.5)
    if i % 2 == 0:
        text(s, px - Inches(0.2), tl_y + tl_h + Inches(0.05),
             Inches(0.6), Inches(0.3),
             f"W{i if i > 0 else 'kickoff'}", size=8, color=MUTED,
             align=PP_ALIGN.CENTER)

# Phase bands
def band(label, headline, x_start, x_end, color, body_y):
    px1 = tl_x + Emu(int(tl_w * (x_start / 13)))
    px2 = tl_x + Emu(int(tl_w * (x_end / 13)))
    rect(s, px1, tl_y + Inches(0.05), px2 - px1, tl_h - Inches(0.1), color)
    text(s, px1 + Inches(0.1), tl_y + Inches(0.13),
         px2 - px1 - Inches(0.2), Inches(0.3),
         label, size=10, bold=True, color=WHITE)

band("P0  Emergency",    "",  0, 1, ACCENT,    None)
band("P1  Technical",    "",  1, 4, PRIMARY,   None)
band("P2  E-E-A-T",      "",  4, 8, PRIMARY_2, None)
band("P3  Entity & GEO", "",  8, 13, RGBColor(0x6E, 0xA8, 0xA8), None)

# Phase cards under timeline
def phase_card(x, w, color, code, name, when, goal):
    y = Inches(3.6)
    h = Inches(3.0)
    rect(s, x, y, w, h, WASH)
    rect(s, x, y, w, Inches(0.5), color)
    text(s, x + Inches(0.2), y + Inches(0.1), w - Inches(0.4), Inches(0.3),
         f"{code}  ·  {when}", size=10, bold=True, color=WHITE)
    text(s, x + Inches(0.2), y + Inches(0.6), w - Inches(0.4), Inches(0.4),
         name, size=14, bold=True, color=PRIMARY)
    text(s, x + Inches(0.2), y + Inches(1.0), w - Inches(0.4), h - Inches(1.1),
         goal, size=11, color=INK)

cw = Inches(2.95)
g = Inches(0.13)
x0 = Inches(0.55)
phase_card(x0,                       cw, ACCENT,
           "PHASE 0", "Emergency unblock", "Days 0–7",
           "Site returns 200 to crawlers. Baseline measurement becomes possible.")
phase_card(x0 + (cw + g),            cw, PRIMARY,
           "PHASE 1", "Technical & local", "Weeks 2–5",
           "Clean, indexable, schema-rich, locally-optimized site — once crawlers can read it.")
phase_card(x0 + 2 * (cw + g),        cw, PRIMARY_2,
           "PHASE 2", "E-E-A-T & content", "Weeks 5–9",
           "Medical-grade trust signals plus the first wave of citation-shaped pillars.")
phase_card(x0 + 3 * (cw + g),        cw, RGBColor(0x6E, 0xA8, 0xA8),
           "PHASE 3", "Entity & GEO scale", "Weeks 9–13",
           "LLMs reliably recognize and cite the clinic. Durable monthly measurement loop.")


# ==========================================================================
# 08 — Phase 0 detail
# ==========================================================================
def phase_detail(code, title_str, when, color, goal, rows_data, exit_str):
    s = add_slide()
    p, t = step()
    slide_chrome(s, f"07–10  ·  {code} detail", p, t,
                 title=f"{code} — {title_str}")
    # Goal banner
    rect(s, Inches(0.55), Inches(1.7), Inches(12.23), Inches(0.55), color)
    text(s, Inches(0.8), Inches(1.78), Inches(11.7), Inches(0.4),
         f"{when}   ·   GOAL: {goal}",
         size=12, bold=True, color=WHITE)

    # Table
    table_cols = [Inches(0.7), Inches(7.2), Inches(2.0), Inches(2.33)]
    xs = [Inches(0.55)]
    for c in table_cols[:-1]:
        xs.append(xs[-1] + c)

    y0 = Inches(2.5)
    row_h = Inches(0.4)
    # header
    cell(s, xs[0], y0, table_cols[0], row_h, "#",      bg=PRIMARY, color=WHITE, bold=True, size=11, align=PP_ALIGN.CENTER)
    cell(s, xs[1], y0, table_cols[1], row_h, "Action", bg=PRIMARY, color=WHITE, bold=True, size=11)
    cell(s, xs[2], y0, table_cols[2], row_h, "Owner",  bg=PRIMARY, color=WHITE, bold=True, size=11, align=PP_ALIGN.CENTER)
    cell(s, xs[3], y0, table_cols[3], row_h, "Effort", bg=PRIMARY, color=WHITE, bold=True, size=11, align=PP_ALIGN.CENTER)

    y = y0 + row_h
    for i, (num, action, owner, effort) in enumerate(rows_data):
        bg = WASH if i % 2 == 0 else WHITE
        # effort pill color
        eff_color = ACCENT if effort.startswith("L") else (ACCENT_2 if effort.startswith("M") else PRIMARY_2)
        cell(s, xs[0], y, table_cols[0], row_h, num,    bg=bg, size=10, align=PP_ALIGN.CENTER, color=MUTED)
        cell(s, xs[1], y, table_cols[1], row_h, action, bg=bg, size=10.5)
        cell(s, xs[2], y, table_cols[2], row_h, owner,  bg=bg, size=10, align=PP_ALIGN.CENTER, color=MUTED)
        cell(s, xs[3], y, table_cols[3], row_h, effort, bg=bg, size=10, bold=True, align=PP_ALIGN.CENTER, color=eff_color)
        y += row_h

    # Exit criteria
    y += Inches(0.1)
    rect(s, Inches(0.55), y, Inches(12.23), Inches(0.85), WASH)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(0.85), color)
    text(s, Inches(0.8), y + Inches(0.1), Inches(11.7), Inches(0.3),
         "EXIT CRITERIA", size=10, bold=True, color=color)
    text(s, Inches(0.8), y + Inches(0.4), Inches(11.7), Inches(0.5),
         exit_str, size=12, color=INK)


phase_detail(
    "PHASE 0", "Emergency unblock", "Days 0–7", ACCENT,
    "Site returns 200 to all crawlers; baseline measurement becomes possible.",
    [
        ("0.1", "Locate and remove the host_not_allowed edge / WAF / origin rule",                "DevOps",          "S ≤1d"),
        ("0.2", "Ensure robots.txt returns 200 (serve as static, outside gated path)",            "DevOps",          "S ≤1d"),
        ("0.3", "Ensure sitemap.xml returns 200 and is current",                                  "DevOps",          "S ≤1d"),
        ("0.4", "Publish AI-bot-friendly robots.txt (allow major answer engines)",                "DevOps + GEO",    "S ≤1d"),
        ("0.5", "Publish initial llms.txt at root",                                               "GEO",             "S ≤1d"),
        ("0.6", "GSC: URL Inspection live test; resubmit sitemap; request indexing of top 10 URLs", "SEO",           "S ≤1d"),
        ("0.7", "Bing Webmaster Tools: submit sitemap (powers Copilot / ChatGPT retrieval)",      "SEO",             "S ≤1d"),
        ("0.8", "Add a synthetic Googlebot-UA probe to monitoring (external IP)",                 "DevOps",          "S ≤1d"),
        ("0.9", "Baseline: full crawl audit + tracked-query battery across ChatGPT/Perplexity/AIO/Gemini/Claude", "SEO + GEO", "M 2–5d"),
    ],
    "All key URLs return 200; sitemap + robots + llms.txt live; GSC fetching successfully; baseline audits captured.",
)


# ==========================================================================
# 09 — Phase 1 detail
# ==========================================================================
phase_detail(
    "PHASE 1", "Technical & local foundations", "Weeks 2–5", PRIMARY,
    "Clean, indexable, schema-rich, locally-optimized site.",
    [
        ("1.1", "Full on-page audit: titles, meta, H-structure, canonicals, hreflang TH↔EN, alt text", "SEO",          "M 2–5d"),
        ("1.2", "Fix canonical + hreflang pairing across all TH/EN equivalents",                       "SEO + Dev",    "M 2–5d"),
        ("1.3", "Core Web Vitals pass: LCP <2.5s, INP <200ms, CLS <0.1 on mobile",                     "Dev",          "L 1–3w"),
        ("1.4", "Site-wide schema: MedicalClinic/Dentist, Organization + sameAs, BreadcrumbList",      "SEO + Dev",    "M 2–5d"),
        ("1.5", "Per-service-page MedicalProcedure schema (howPerformed, preparation, followup)",      "SEO + Dev",    "M 2–5d"),
        ("1.6", "Google Business Profile per branch + NAP consistency audit",                          "SEO",          "M 2–5d"),
        ("1.7", "Local citations cleanup across Thai + medical-tourism directories",                   "SEO",          "M 2–5d"),
        ("1.8", "Internal-link graph: eliminate orphan service pages; pillar↔supporting",              "SEO + Content","M 2–5d"),
        ("1.9", "Fix any noindex / X-Robots-Tag leakage; confirm clean response headers",              "Dev",          "S ≤1d"),
    ],
    "Zero P0/P1 technical issues open; schema validates; CWV \"Good\"; GBP complete per branch; no orphan service pages.",
)


# ==========================================================================
# 10 — Phase 2 detail
# ==========================================================================
phase_detail(
    "PHASE 2", "E-E-A-T & content engine", "Weeks 5–9", PRIMARY_2,
    "Medical-grade trust signals + first wave of citation-shaped content.",
    [
        ("2.1", "Doctor profile pages with Person schema (credentials, worksFor, sameAs)",            "Content + SEO",        "M 2–5d"),
        ("2.2", "Add reviewer byline + reviewedBy + visible lastReviewed date to all YMYL pages",     "Content",              "M 2–5d"),
        ("2.3", "Confirm clinic facts (services, prices, brands stocked, branches) — unblocks content","Client",              "S ≤1d"),
        ("2.4", "Publish priority-cluster pillar + supporting content via brief→draft→review→revise", "Planner→Creator→SEO+GEO","L 1–3w"),
        ("2.5", "Convert top revenue pages to citation shape (answer-first, Q-H2s, tables, FAQ)",     "Creator + GEO",        "L 1–3w"),
        ("2.6", "Wire FAQPage schema to every Q&A block",                                             "SEO + Dev",            "M 2–5d"),
        ("2.7", "Begin Thai-language adaptations (native-speaker reviewed) of best EN pieces",        "Creator",              "M 2–5d"),
    ],
    "Doctor profiles live; YMYL pages carry reviewer signals; one citation-optimized pillar live per top cluster; sample implant-cost guide finalized.",
)


# ==========================================================================
# 11 — Phase 3 detail
# ==========================================================================
phase_detail(
    "PHASE 3", "Entity footprint, GEO scale & measurement", "Weeks 9–13",
    RGBColor(0x6E, 0xA8, 0xA8),
    "LLMs reliably recognize and cite the clinic; durable measurement loop established.",
    [
        ("3.1", "File Wikidata entry (Organization + sameAs to GBP, LinkedIn, FB, IG)",            "GEO",                 "M 2–5d"),
        ("3.2", "Consistent entity profile across DentaVox, WhatClinic, Dental Departures, Bookimed", "GEO + Marketing",   "M 2–5d"),
        ("3.3", "Publish llms-full.txt with condensed high-value content",                         "GEO",                 "M 2–5d"),
        ("3.4", "Original-data asset (e.g. anonymized 2025 price ranges / brand mix)",             "GEO + Client",        "M 2–5d"),
        ("3.5", "Drive Perplexity / AIO discovery via social signals to key pages",                "Marketing",           "S ≤1d"),
        ("3.6", "Monthly tracked-query battery (top 20 questions, TH+EN) → citation share",        "GEO",                 "M 2–5d"),
        ("3.7", "Quarterly roadmap: convert audit deltas into next content calendar",              "Planner",             "M 2–5d"),
    ],
    "Wikidata + directory entity consistency live; llms-full.txt published; first original-data asset live; monthly AI-citation tracking running with delta.",
)


# ==========================================================================
# 12 — KPIs table
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "11  ·  KPIs", p, t,
             title="What success looks like at Day 30, 60, 90.")

table_cols = [Inches(4.2), Inches(2.4), Inches(1.85), Inches(1.85), Inches(1.93)]
xs = [Inches(0.55)]
for c in table_cols[:-1]:
    xs.append(xs[-1] + c)

y0 = Inches(1.85)
row_h = Inches(0.5)
headers = ["Metric", "Baseline (today)", "Day 30", "Day 60", "Day 90"]
for i, hd in enumerate(headers):
    cell(s, xs[i], y0, table_cols[i], row_h, hd,
         bg=PRIMARY, color=WHITE, bold=True, size=11,
         align=PP_ALIGN.LEFT if i == 0 else PP_ALIGN.CENTER)

rows = [
    ("Crawlable URLs (HTTP 200)",                     "~0% (403)",            "100%",          "100%",                       "100%"),
    ("Pages indexed (GSC)",                           "Unknown / decaying",   "Recovering",    "Back to pre-block + new",    "Growth trend"),
    ("Service pages with valid schema",               "Unknown",              "Core types live", "All service pages",        "All pages"),
    ("Branches with complete GBP",                    "TBD",                  "Audited",       "Complete",                   "Optimized + posting"),
    ("YMYL pages with reviewer signals",              "~0",                   "Template live", "50%",                        "100%"),
    ("Citation-optimized pillars published",          "0 (1 draft)",          "1",             "3",                          "5 (one per cluster)"),
    ("AI-citation share (tracked queries)",           "~0 (unreachable)",     "Baseline set",  "First citations",            "Measurable share"),
    ("Core Web Vitals (mobile)",                      "Unmeasurable",         "Measured",      "Improving",                  "All \"Good\""),
]
y = y0 + row_h
for i, row in enumerate(rows):
    bg = WASH if i % 2 == 0 else WHITE
    for j, val in enumerate(row):
        bold = (j == 0)
        cell(s, xs[j], y, table_cols[j], row_h, val,
             bg=bg, size=10.5, bold=bold,
             align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER,
             color=INK if j != 0 else PRIMARY)
    y += row_h

# Cadence note
y += Inches(0.05)
text(s, Inches(0.55), y, Inches(12.23), Inches(0.35),
     "Review cadence: weekly during Phase 0–1; bi-weekly during Phase 2–3. Monthly KPI report to client.",
     size=11, italic=True, color=MUTED)


# ==========================================================================
# 13 — Dependencies & risks
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "12  ·  Dependencies & risks", p, t,
             title="What could slow us down — and how we mitigate it.")

table_cols = [Inches(5.6), Inches(2.4), Inches(4.23)]
xs = [Inches(0.55)]
for c in table_cols[:-1]:
    xs.append(xs[-1] + c)

y0 = Inches(1.85)
row_h = Inches(0.5)

cell(s, xs[0], y0, table_cols[0], row_h, "Dependency / risk", bg=PRIMARY, color=WHITE, bold=True, size=11)
cell(s, xs[1], y0, table_cols[1], row_h, "Impact",            bg=PRIMARY, color=WHITE, bold=True, size=11, align=PP_ALIGN.CENTER)
cell(s, xs[2], y0, table_cols[2], row_h, "Mitigation",        bg=PRIMARY, color=WHITE, bold=True, size=11)

rows = [
    ("DevOps access to CDN / WAF / origin config",                      "Blocks everything",     "Escalate today; Phase 0 cannot start without it"),
    ("Client confirmation of services / prices / brands / branches",    "Blocks content (P2)",   "Collect in week 1, in parallel with Phase 0"),
    ("Search Console + GA4 access",                                     "Blocks measurement",    "Request access now"),
    ("Thai native-speaker review capacity",                             "Blocks TH publishing",  "Identify reviewer in week 1"),
    ("Doctor credentials + photos for bylines",                         "Blocks E-E-A-T",        "Collect during Phase 1"),
    ("The 403 recurs after fix (config not durable)",                   "Re-extinction",         "Synthetic Googlebot probe + static robots.txt"),
]
y = y0 + row_h
for i, (a, b, c) in enumerate(rows):
    bg = WASH if i % 2 == 0 else WHITE
    cell(s, xs[0], y, table_cols[0], row_h, a, bg=bg, size=11)
    cell(s, xs[1], y, table_cols[1], row_h, b, bg=bg, size=10.5, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    cell(s, xs[2], y, table_cols[2], row_h, c, bg=bg, size=11)
    y += row_h


# ==========================================================================
# 14 — This-week actions (callout)
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "13  ·  This week", p, t,
             title="Five moves to start right now.")

def action_row(idx, y, owner, owner_color, text_str):
    # Numbered chip
    chip = slide_chrome  # placeholder to silence linter
    rect(s, Inches(0.55), y, Inches(0.6), Inches(0.6), PRIMARY)
    text(s, Inches(0.55), y, Inches(0.6), Inches(0.6),
         str(idx), size=20, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # Owner tag
    rect(s, Inches(1.35), y + Inches(0.13), Inches(1.5), Inches(0.34), owner_color)
    text(s, Inches(1.35), y + Inches(0.13), Inches(1.5), Inches(0.34),
         owner, size=10, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # Text
    text(s, Inches(3.0), y + Inches(0.05), Inches(9.8), Inches(0.5),
         text_str, size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE)

ay = Inches(1.85)
gap_y = Inches(0.92)
action_row(1, ay,                 "DEVOPS",        ACCENT,
           "Remove the host_not_allowed edge rule; verify HTTP 200 for browser + Googlebot + GPTBot. (today)")
action_row(2, ay + gap_y,         "DEVOPS + GEO",  PRIMARY,
           "Publish corrected robots.txt, sitemap.xml, and llms.txt. (Day 0–1)")
action_row(3, ay + 2 * gap_y,     "SEO",           PRIMARY_2,
           "Resubmit sitemap and request reindexing in Google Search Console + Bing. (Day 1–2)")
action_row(4, ay + 3 * gap_y,     "CLIENT",        ACCENT_2,
           "Start compiling confirmed services, prices, implant / aligner brands, branches, doctor credentials. (week 1)")
action_row(5, ay + 4 * gap_y,     "SEO + GEO",     RGBColor(0x6E, 0xA8, 0xA8),
           "Capture baseline crawl audit + AI tracked-query battery once the site is reachable. (Day 3–5)")


# ==========================================================================
# 15 — Roles & RACI (compact)
# ==========================================================================
s = add_slide()
p, t = step()
slide_chrome(s, "14  ·  Roles", p, t,
             title="Who does what across the program.")

cols = ["Role", "Primary responsibilities", "Stage"]
table_cols = [Inches(2.0), Inches(8.4), Inches(1.83)]
xs = [Inches(0.55)]
for c in table_cols[:-1]:
    xs.append(xs[-1] + c)

y0 = Inches(1.85)
row_h = Inches(0.55)

for i, hd in enumerate(cols):
    cell(s, xs[i], y0, table_cols[i], row_h, hd,
         bg=PRIMARY, color=WHITE, bold=True, size=11)

rows = [
    ("Client",       "Approve facts (services, prices, brands, doctor credentials, branches); grant GSC/GA4 access; sign-off content.", "All"),
    ("DevOps",       "Remove edge block, manage robots/sitemap/llms.txt, fix CWV, deploy schema, run synthetic crawler probe.",          "P0–P1"),
    ("SEO expert",   "Audits, on-page and local SEO, schema design, internal links, GBP optimization, KPI tracking.",                    "All"),
    ("GEO expert",   "Crawler-allowlist policy, llms.txt/llms-full.txt, entity footprint, citation-shape requirements, AI-citation monitoring.", "All"),
    ("Content planner", "Cluster map, keyword registry, calendar, briefs, backlog prioritization.",                                       "P2–P3"),
    ("Content creator", "Drafts and revises copy in TH + EN; executes briefs from planner with SEO + GEO requirements.",                  "P2–P3"),
    ("Native-speaker reviewer", "Reviews all Thai-language copy before publish.",                                                         "P2–P3"),
]
y = y0 + row_h
for i, (a, b, c) in enumerate(rows):
    bg = WASH if i % 2 == 0 else WHITE
    cell(s, xs[0], y, table_cols[0], row_h, a, bg=bg, size=11, bold=True, color=PRIMARY)
    cell(s, xs[1], y, table_cols[1], row_h, b, bg=bg, size=11)
    cell(s, xs[2], y, table_cols[2], row_h, c, bg=bg, size=11, bold=True, color=PRIMARY_2, align=PP_ALIGN.CENTER)
    y += row_h


# ==========================================================================
# 16 — Closing
# ==========================================================================
s = add_slide()
# Same cover-style framing
rect(s, Emu(0), Emu(0), Inches(4.6), SLIDE_H, PRIMARY)
rect(s, Inches(4.6), Emu(0), SLIDE_W - Inches(4.6), SLIDE_H, WHITE)
rect(s, Inches(4.6), Emu(0), Inches(0.08), SLIDE_H, ACCENT)

text(s, Inches(0.6), Inches(0.55), Inches(4), Inches(0.4),
     "THE DENT  ·  BANGKOK", size=11, bold=True, color=WHITE)

text(s, Inches(0.6), Inches(2.8), Inches(3.6), Inches(0.5),
     "AGENCY", size=11, bold=True, color=ACCENT_2)
text(s, Inches(0.6), Inches(3.2), Inches(3.6), Inches(2.2),
     ["SEO & GEO",
      "Agent Orchestra"],
     size=24, bold=True, color=WHITE)

# Right
text(s, Inches(5.1), Inches(1.4), Inches(7.6), Inches(0.4),
     "NEXT STEP", size=11, bold=True, color=PRIMARY_2)
text(s, Inches(5.1), Inches(1.85), Inches(7.8), Inches(1.6),
     ["Clear the block.",
      "Then we build."],
     size=40, bold=True, color=PRIMARY)
text(s, Inches(5.1), Inches(3.6), Inches(7.8), Inches(0.5),
     "Once thedent.co.th returns 200 to crawlers, the 90-day plan executes on schedule.",
     size=15, color=INK)

# Deliverables list
line(s, Inches(5.1), Inches(4.5), Inches(12.7), Inches(4.5))
text(s, Inches(5.1), Inches(4.65), Inches(7.6), Inches(0.4),
     "Deliverables already in workspace/", size=11, bold=True, color=PRIMARY_2)
bullets(s, Inches(5.1), Inches(5.0), Inches(7.6), Inches(2.2),
        ["plans/2026-04-19-remediation-report-90day-plan.md — the long-form report",
         "seo-audits/2026-04-19-thedent-live-audit.md — live SEO findings",
         "geo-audits/2026-04-19-thedent-live-audit.md — live GEO findings + ready-to-paste robots.txt + llms.txt",
         "content/en/dental-implants-cost-bangkok-2026.md — sample citation-shaped pillar",
         "plans/calendar-2026-W17.md — example weekly editorial calendar"],
        size=11, color=INK, spacing=4)


# --------------------------------------------------------------------------
prs.save(OUT_PATH)
print(f"Saved: {OUT_PATH}  ({OUT_PATH.stat().st_size:,} bytes)")
