#!/usr/bin/env python3
"""
build-slides.py — figma-ppt HTML Slide Builder

Reads slides-plan.json and generates a multi-page HTML/CSS website.
Each slide = a standalone 1920×1080 HTML page.
Pages are served locally and captured via generate_figma_design into Figma.

Usage:
  python build-slides.py \
    --slides-plan ./slides-plan.json \
    --output-dir  ./slide-output
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────
# SHARED CSS (injected into every slide page)
# ─────────────────────────────────────────────────────────────

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500;700&family=Cormorant+Garamond:ital,wght@0,300;0,600;1,300&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --primary:       %(primary)s;
  --background:    %(background)s;
  --surface:       %(surface)s;
  --accent:        %(accent)s;
  --text-primary:  %(textPrimary)s;
  --text-secondary:%(textSecondary)s;
  --font-display:  '%(fontDisplay)s', Inter, sans-serif;
  --font-body:     '%(fontBody)s', Inter, sans-serif;
}

html, body {
  width:  1920px;
  height: 1080px;
  overflow: hidden;
  background: var(--background);
  color: var(--text-primary);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* ── Utility ── */
.slide {
  width: 1920px;
  height: 1080px;
  position: relative;
  overflow: hidden;
  background: var(--background);
}

/* accent stripe */
.accent-stripe {
  position: absolute;
  left: 0; top: 0;
  width: 6px; height: 100%%;
  background: var(--primary);
}

/* section label */
.section-label {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--primary);
  margin-bottom: 16px;
}

/* slide number watermark */
.slide-num {
  position: absolute;
  right: 64px;
  bottom: 48px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.08em;
  opacity: 0.5;
}
"""

# ─────────────────────────────────────────────────────────────
# SLIDE HTML BUILDERS — one function per slide type
# ─────────────────────────────────────────────────────────────

def slide_hero(c, idx, palette, fonts):
    title    = c.get("title", "")
    subtitle = c.get("subtitle", "")
    tagline  = c.get("tagline", "")
    author   = c.get("author", "")
    date     = c.get("date", "")

    return f"""
<div class="slide slide-hero">
  <!-- Left color panel -->
  <div class="hero-panel-left">
    {f'<div class="hero-tagline">{tagline}</div>' if tagline else ''}
    <h1 class="hero-title">{title}</h1>
    <div class="hero-rule"></div>
    <div class="hero-meta">
      {f'<span class="hero-author">{author}</span>' if author else ''}
      {f'<span class="hero-sep">·</span><span class="hero-date">{date}</span>' if date and author else f'<span class="hero-date">{date}</span>' if date else ''}
    </div>
  </div>

  <!-- Right content panel -->
  <div class="hero-panel-right">
    {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
    <div class="hero-deco-num">01</div>
  </div>

  <!-- Corner accent -->
  <div class="hero-corner-accent"></div>
</div>

<style>
.slide-hero {{
  display: flex;
}}
.hero-panel-left {{
  width: 55%;
  height: 100%;
  background: var(--primary);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 96px;
  position: relative;
}}
.hero-tagline {{
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.65);
  margin-bottom: 32px;
}}
.hero-title {{
  font-family: var(--font-display);
  font-size: 80px;
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -2px;
  color: #ffffff;
  margin-bottom: 48px;
}}
.hero-rule {{
  width: 64px;
  height: 3px;
  background: rgba(255,255,255,0.4);
  margin-bottom: 32px;
}}
.hero-meta {{
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: rgba(255,255,255,0.75);
  font-weight: 400;
}}
.hero-sep {{ opacity: 0.4; }}
.hero-panel-right {{
  flex: 1;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 96px 80px;
  position: relative;
}}
.hero-subtitle {{
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 300;
  line-height: 1.4;
  color: var(--text-primary);
  max-width: 520px;
}}
.hero-deco-num {{
  position: absolute;
  right: 64px;
  bottom: 64px;
  font-size: 160px;
  font-weight: 800;
  color: var(--primary);
  opacity: 0.06;
  line-height: 1;
  font-family: var(--font-display);
}}
.hero-corner-accent {{
  position: absolute;
  bottom: 0;
  left: 55%;
  transform: translateX(-50%);
  width: 2px;
  height: 80px;
  background: var(--primary);
  opacity: 0.3;
}}
</style>
"""


def slide_agenda(c, idx, palette, fonts):
    heading      = c.get("heading", "Agenda")
    section_label = c.get("sectionLabel", "OVERVIEW")
    items        = c.get("items", [])

    items_html = ""
    for i, item in enumerate(items):
        num = f"{i+1:02d}"
        items_html += f"""
        <div class="agenda-item">
          <span class="agenda-num">{num}</span>
          <span class="agenda-divider"></span>
          <span class="agenda-text">{item}</span>
        </div>"""

    return f"""
<div class="slide slide-agenda">
  <div class="accent-stripe"></div>

  <div class="agenda-content">
    <div class="section-label">{section_label}</div>
    <h2 class="agenda-heading">{heading}</h2>
    <div class="agenda-items">
      {items_html}
    </div>
  </div>

  <div class="slide-num">{idx:02d}</div>
</div>

<style>
.slide-agenda {{
  display: flex;
  align-items: center;
  padding-left: 120px;
}}
.agenda-content {{
  width: 100%;
  max-width: 1400px;
}}
.agenda-heading {{
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 700;
  letter-spacing: -1.5px;
  color: var(--text-primary);
  margin-bottom: 64px;
  line-height: 1.1;
}}
.agenda-items {{
  display: flex;
  flex-direction: column;
  gap: 0;
}}
.agenda-item {{
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 24px 0;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}}
.agenda-item:first-child {{
  border-top: 1px solid rgba(255,255,255,0.07);
}}
.agenda-num {{
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  min-width: 36px;
  letter-spacing: 0.05em;
}}
.agenda-divider {{
  width: 1px;
  height: 24px;
  background: rgba(255,255,255,0.15);
}}
.agenda-text {{
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}}
</style>
"""


def slide_content(c, idx, palette, fonts):
    heading      = c.get("heading", "")
    section_label = c.get("sectionLabel", "")
    body         = c.get("body", "")
    bullets      = c.get("bullets", [])
    has_image    = bool(c.get("imageHint"))

    bullets_html = ""
    for b in bullets:
        bullets_html += f'<li class="content-bullet">{b}</li>'

    image_html = ""
    if has_image:
        image_html = f"""
        <div class="content-image-placeholder">
          <span class="content-image-hint">{c.get('imageHint', '')}</span>
        </div>"""

    layout_class = "content-layout-split" if has_image else "content-layout-full"

    return f"""
<div class="slide slide-content">
  <!-- Header bar -->
  <div class="content-header">
    {f'<div class="section-label">{section_label}</div>' if section_label else ''}
    <h2 class="content-heading">{heading}</h2>
  </div>

  <!-- Body area -->
  <div class="content-body {layout_class}">
    <div class="content-text">
      {f'<p class="content-body-text">{body}</p>' if body else ''}
      {f'<ul class="content-bullets">{bullets_html}</ul>' if bullets else ''}
    </div>
    {image_html}
  </div>

  <div class="slide-num">{idx:02d}</div>
</div>

<style>
.slide-content {{
  display: flex;
  flex-direction: column;
}}
.content-header {{
  padding: 64px 96px 48px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  background: var(--surface);
}}
.content-heading {{
  font-family: var(--font-display);
  font-size: 52px;
  font-weight: 700;
  letter-spacing: -1.5px;
  line-height: 1.1;
  color: var(--text-primary);
}}
.content-body {{
  flex: 1;
  padding: 56px 96px;
  display: flex;
  gap: 80px;
}}
.content-layout-full .content-text {{ max-width: 1100px; }}
.content-layout-split .content-text {{ width: 55%; }}
.content-body-text {{
  font-size: 22px;
  line-height: 1.65;
  color: var(--text-secondary);
  margin-bottom: 36px;
  font-weight: 400;
}}
.content-bullets {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
}}
.content-bullet {{
  font-size: 24px;
  line-height: 1.5;
  color: var(--text-primary);
  font-weight: 400;
  padding-left: 28px;
  position: relative;
}}
.content-bullet::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 13px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
}}
.content-image-placeholder {{
  flex: 1;
  background: var(--surface);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}}
.content-image-hint {{
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  max-width: 240px;
  opacity: 0.5;
}}
</style>
"""


def slide_two_col(c, idx, palette, fonts):
    heading      = c.get("heading", "")
    section_label = c.get("sectionLabel", "")
    left         = c.get("leftCol", {})
    right        = c.get("rightCol", {})

    def col_html(col):
        h     = col.get("heading", "")
        body  = col.get("body", "")
        items = col.get("bullets", [])
        bullets = "".join(f'<li class="col-bullet">{b}</li>' for b in items)
        return f"""
        <div class="twocol-card">
          <h3 class="col-heading">{h}</h3>
          {f'<p class="col-body">{body}</p>' if body else ''}
          {f'<ul class="col-bullets">{bullets}</ul>' if items else ''}
        </div>"""

    return f"""
<div class="slide slide-twocol">
  <div class="content-header">
    {f'<div class="section-label">{section_label}</div>' if section_label else ''}
    <h2 class="content-heading">{heading}</h2>
  </div>

  <div class="twocol-body">
    {col_html(left)}
    {col_html(right)}
  </div>

  <div class="slide-num">{idx:02d}</div>
</div>

<style>
.slide-twocol {{
  display: flex;
  flex-direction: column;
}}
.twocol-body {{
  flex: 1;
  display: flex;
  gap: 32px;
  padding: 48px 96px;
  align-items: stretch;
}}
.twocol-card {{
  flex: 1;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.07);
  border-left: 4px solid var(--primary);
  padding: 48px 52px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}}
.col-heading {{
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--text-primary);
}}
.col-body {{
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}}
.col-bullets {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}}
.col-bullet {{
  font-size: 20px;
  color: var(--text-primary);
  padding-left: 24px;
  position: relative;
  line-height: 1.4;
}}
.col-bullet::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
}}
</style>
"""


def slide_stats(c, idx, palette, fonts):
    heading      = c.get("heading", "")
    section_label = c.get("sectionLabel", "")
    stats        = c.get("stats", [])

    cards_html = ""
    for s in stats:
        trend_html = f'<div class="stat-trend">{s["trend"]}</div>' if s.get("trend") else ""
        desc_html  = f'<div class="stat-desc">{s["description"]}</div>' if s.get("description") else ""
        cards_html += f"""
        <div class="stat-card">
          <div class="stat-number">{s.get("number","")}</div>
          <div class="stat-label">{s.get("label","")}</div>
          {trend_html}
          {desc_html}
        </div>"""

    return f"""
<div class="slide slide-stats">
  <div class="content-header">
    {f'<div class="section-label">{section_label}</div>' if section_label else ''}
    <h2 class="content-heading">{heading}</h2>
  </div>

  <div class="stats-body">
    {cards_html}
  </div>

  <div class="slide-num">{idx:02d}</div>
</div>

<style>
.slide-stats {{
  display: flex;
  flex-direction: column;
}}
.stats-body {{
  flex: 1;
  display: flex;
  gap: 24px;
  padding: 48px 96px;
  align-items: stretch;
}}
.stat-card {{
  flex: 1;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.07);
  padding: 52px 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}}
.stat-number {{
  font-family: var(--font-display);
  font-size: 80px;
  font-weight: 800;
  letter-spacing: -3px;
  line-height: 1;
  color: var(--primary);
}}
.stat-label {{
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-secondary);
}}
.stat-trend {{
  font-size: 18px;
  font-weight: 600;
  color: #4ade80;
}}
.stat-desc {{
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-top: 4px;
  opacity: 0.7;
}}
</style>
"""


def slide_quote(c, idx, palette, fonts):
    quote        = c.get("quote", "")
    attribution  = c.get("attribution", "")
    role         = c.get("role", "")

    return f"""
<div class="slide slide-quote">
  <!-- Full-bleed primary background -->
  <div class="quote-bg"></div>

  <!-- Giant decorative quote mark -->
  <div class="quote-deco">"</div>

  <div class="quote-content">
    <blockquote class="quote-text">{quote}</blockquote>
    <div class="quote-rule"></div>
    <div class="quote-attribution">
      {f'<span class="quote-name">{attribution}</span>' if attribution else ''}
      {f'<span class="quote-role">{role}</span>' if role else ''}
    </div>
  </div>

  <div class="slide-num" style="color: rgba(255,255,255,0.3);">{idx:02d}</div>
</div>

<style>
.slide-quote {{
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary) !important;
}}
.quote-bg {{
  position: absolute;
  inset: 0;
  background: var(--primary);
}}
.quote-deco {{
  position: absolute;
  top: 60px;
  left: 80px;
  font-family: var(--font-display);
  font-size: 240px;
  font-weight: 800;
  color: rgba(255,255,255,0.08);
  line-height: 1;
  pointer-events: none;
}}
.quote-content {{
  position: relative;
  max-width: 1200px;
  text-align: center;
  padding: 0 96px;
}}
.quote-text {{
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 400;
  line-height: 1.4;
  color: #ffffff;
  letter-spacing: -0.5px;
  margin-bottom: 56px;
  font-style: italic;
}}
.quote-rule {{
  width: 64px;
  height: 2px;
  background: rgba(255,255,255,0.35);
  margin: 0 auto 32px;
}}
.quote-attribution {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}}
.quote-name {{
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.03em;
}}
.quote-role {{
  font-size: 15px;
  color: rgba(255,255,255,0.6);
  letter-spacing: 0.05em;
}}
</style>
"""


def slide_divider(c, idx, palette, fonts):
    num   = c.get("sectionNumber", idx)
    title = c.get("sectionTitle", "")
    desc  = c.get("description", "")

    return f"""
<div class="slide slide-divider">
  <!-- Left panel -->
  <div class="div-left">
    <div class="div-big-num">{num:02d}</div>
  </div>

  <!-- Right panel -->
  <div class="div-right">
    <div class="section-label" style="color: var(--primary);">SECTION {num:02d}</div>
    <h2 class="div-title">{title}</h2>
    {f'<p class="div-desc">{desc}</p>' if desc else ''}
  </div>
</div>

<style>
.slide-divider {{
  display: flex;
}}
.div-left {{
  width: 45%;
  height: 100%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}}
.div-big-num {{
  font-family: var(--font-display);
  font-size: 320px;
  font-weight: 900;
  color: rgba(0,0,0,0.15);
  line-height: 1;
  user-select: none;
}}
.div-right {{
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 96px 96px 96px 80px;
}}
.div-title {{
  font-family: var(--font-display);
  font-size: 64px;
  font-weight: 700;
  letter-spacing: -2px;
  line-height: 1.05;
  color: var(--text-primary);
  margin: 20px 0 32px;
}}
.div-desc {{
  font-size: 22px;
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 560px;
}}
</style>
"""


def slide_closing(c, idx, palette, fonts):
    tagline    = c.get("tagline", "THANK YOU")
    heading    = c.get("heading", "Let's Build Together")
    subheading = c.get("subheading", "")
    takeaways  = c.get("keyTakeaways", [])
    cta        = c.get("cta", "")
    contact    = c.get("contactInfo", "")

    takeaway_html = ""
    for t in takeaways:
        takeaway_html += f'<li class="closing-takeaway"><span class="takeaway-check">✓</span>{t}</li>'

    return f"""
<div class="slide slide-closing">
  <!-- Full-bleed background -->
  <!-- Decorative circles -->
  <div class="closing-circle c1"></div>
  <div class="closing-circle c2"></div>

  <div class="closing-left">
    <div class="closing-tagline">{tagline}</div>
    <h1 class="closing-heading">{heading}</h1>
    {f'<p class="closing-subheading">{subheading}</p>' if subheading else ''}
    {f'<div class="closing-cta">{cta}</div>' if cta else ''}
  </div>

  {f'''<div class="closing-right">
    <div class="closing-takeaways-label">Key Takeaways</div>
    <ul class="closing-takeaways">{takeaway_html}</ul>
  </div>''' if takeaways else ''}

  {f'<div class="closing-contact">{contact}</div>' if contact else ''}
</div>

<style>
.slide-closing {{
  background: var(--primary) !important;
  display: flex;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}}
.closing-circle {{
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}}
.c1 {{
  width: 800px; height: 800px;
  right: -200px; bottom: -200px;
}}
.c2 {{
  width: 500px; height: 500px;
  right: 200px; top: -150px;
}}
.closing-left {{
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 96px;
}}
.closing-tagline {{
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.6);
  margin-bottom: 24px;
}}
.closing-heading {{
  font-family: var(--font-display);
  font-size: 80px;
  font-weight: 800;
  letter-spacing: -2.5px;
  line-height: 1.05;
  color: #ffffff;
  margin-bottom: 28px;
}}
.closing-subheading {{
  font-size: 24px;
  line-height: 1.5;
  color: rgba(255,255,255,0.75);
  margin-bottom: 48px;
  max-width: 560px;
}}
.closing-cta {{
  font-size: 20px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  padding: 16px 0;
  border-top: 1px solid rgba(255,255,255,0.2);
  display: inline-block;
}}
.closing-right {{
  width: 560px;
  background: rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 64px;
  gap: 32px;
}}
.closing-takeaways-label {{
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
}}
.closing-takeaways {{
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
}}
.closing-takeaway {{
  display: flex;
  align-items: flex-start;
  gap: 16px;
  font-size: 18px;
  line-height: 1.5;
  color: rgba(255,255,255,0.9);
}}
.takeaway-check {{
  color: rgba(255,255,255,0.5);
  flex-shrink: 0;
  font-size: 14px;
  margin-top: 3px;
}}
.closing-contact {{
  position: absolute;
  bottom: 48px;
  left: 96px;
  font-size: 15px;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.05em;
}}
</style>
"""


# ─────────────────────────────────────────────────────────────
# SLIDE TYPE DISPATCH
# ─────────────────────────────────────────────────────────────

BUILDERS = {
    "HERO":    slide_hero,
    "AGENDA":  slide_agenda,
    "CONTENT": slide_content,
    "TWO_COL": slide_two_col,
    "STATS":   slide_stats,
    "QUOTE":   slide_quote,
    "DIVIDER": slide_divider,
    "CLOSING": slide_closing,
}


# ─────────────────────────────────────────────────────────────
# PAGE TEMPLATE
# ─────────────────────────────────────────────────────────────

def make_page(slide_html, css_vars, google_fonts_url, title, slide_num, total):
    """Wrap slide HTML in a full standalone page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920">
  <title>Slide {slide_num} — {title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{google_fonts_url}" rel="stylesheet">
  <style>
{css_vars}
  </style>
</head>
<body>
{slide_html}
</body>
</html>"""


def build_css_vars(palette, fonts):
    """Build :root CSS with palette + font vars."""
    return SHARED_CSS % {
        "primary":       palette.get("primary",       "#2D3FE0"),
        "background":    palette.get("background",    "#0A0A0A"),
        "surface":       palette.get("surface",       "#111111"),
        "accent":        palette.get("accent",        "#FF3B00"),
        "textPrimary":   palette.get("textPrimary",   "#FFFFFF"),
        "textSecondary": palette.get("textSecondary", "#888888"),
        "fontDisplay":   fonts.get("display",         "Inter"),
        "fontBody":      fonts.get("body",            "Inter"),
    }


def build_google_fonts_url(fonts):
    """Generate Google Fonts import URL for both fonts."""
    families = set()
    for v in fonts.values():
        name = v.replace(" ", "+")
        families.add(f"family={name}:wght@300;400;500;600;700;800;900")
    # Always include Inter as fallback
    families.add("family=Inter:wght@300;400;500;600;700;800")
    query = "&".join(sorted(families))
    return f"https://fonts.googleapis.com/css2?{query}&display=swap"


# ─────────────────────────────────────────────────────────────
# INDEX PAGE
# ─────────────────────────────────────────────────────────────

def make_index(title, slide_files):
    links = "\n".join(
        f'    <li><a href="slides/{f}">{f}</a></li>'
        for f in slide_files
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title} — Slide Index</title>
  <style>
    body {{ font-family: sans-serif; background: #0a0a0a; color: #fff; padding: 48px; }}
    h1 {{ font-size: 32px; margin-bottom: 32px; }}
    ul {{ list-style: none; display: flex; flex-direction: column; gap: 12px; }}
    a {{ color: #6b7fff; font-size: 18px; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <ul>
{links}
  </ul>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="figma-ppt: Build HTML slide website from slides-plan.json"
    )
    parser.add_argument("--slides-plan",  default="./slides-plan.json",  help="Path to slides-plan.json")
    parser.add_argument("--output-dir",   default="./slide-output",       help="Output directory")
    args = parser.parse_args()

    plan_path = Path(args.slides_plan)
    out_dir   = Path(args.output_dir)

    # Load plan
    if not plan_path.exists():
        print(f"ERROR: slides-plan.json not found at {plan_path}", file=sys.stderr)
        sys.exit(1)

    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)

    title   = plan.get("title", "Presentation")
    palette = plan.get("palette", {})
    fonts   = plan.get("fonts", {"display": "Inter", "body": "Inter"})
    slides  = plan.get("slides", [])

    if not slides:
        print("ERROR: No slides in plan.", file=sys.stderr)
        sys.exit(1)

    # Prepare directories
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    css_vars         = build_css_vars(palette, fonts)
    google_fonts_url = build_google_fonts_url(fonts)

    slide_files = []
    results     = []

    for i, slide in enumerate(slides, start=1):
        stype   = slide.get("type", "CONTENT").upper()
        content = slide.get("content", {})
        builder = BUILDERS.get(stype)

        if not builder:
            print(f"WARNING: Unknown slide type '{stype}' at index {i}. Skipping.", file=sys.stderr)
            continue

        # Build slide HTML fragment
        slide_html = builder(content, i, palette, fonts)

        # Wrap in full page
        page_html = make_page(
            slide_html    = slide_html,
            css_vars      = css_vars,
            google_fonts_url = google_fonts_url,
            title         = title,
            slide_num     = i,
            total         = len(slides),
        )

        # Write file
        slug = stype.lower().replace("_", "-")
        fname = f"{i:02d}-{slug}.html"
        (slides_dir / fname).write_text(page_html, encoding="utf-8")
        slide_files.append(fname)

        results.append({
            "index": i,
            "type":  stype,
            "file":  fname,
            "url":   f"http://localhost:7890/slides/{fname}",
        })
        print(f"  [{i:02d}] {stype:10s} → slides/{fname}")

    # Write index page
    (out_dir / "index.html").write_text(
        make_index(title, slide_files),
        encoding="utf-8"
    )

    # Write slide-urls.json for the capture script
    urls_path = out_dir / "slide-urls.json"
    with open(urls_path, "w", encoding="utf-8") as f:
        json.dump({"title": title, "slides": results}, f, indent=2, ensure_ascii=False)

    print(f"\n[build-slides] SUCCESS")
    print(f"  Slides:  {len(results)}")
    print(f"  Output:  {out_dir.resolve()}")
    print(f"  Index:   {(out_dir / 'index.html').resolve()}")
    print(f"  URLs:    {urls_path.resolve()}")
    print(f"\nTo serve locally:")
    print(f"  python -m http.server 7890 --directory {out_dir.resolve()}")
    print(f"\nFirst slide: http://localhost:7890/slides/{slide_files[0]}")


if __name__ == "__main__":
    main()
