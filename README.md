# figma-ppt — Claude Code Skill

> Generate Figma presentation slides by building a real **1920×1080 HTML/CSS website** and capturing it into **editable Figma frames** via Claude Code + Figma MCP.

No API keys. No Figma plugin to install. Just Claude Code.

---

## How It Works

```
Your content + tone
        ↓  (Claude plans)
  slides-plan.json         ← structured slide plan

        ↓  (build-slides.py)
  slide-output/            ← real HTML/CSS website
    slides/01-hero.html
    slides/02-agenda.html
    ...

        ↓  (Python HTTP server)
  localhost:7890           ← slides served locally

        ↓  (generate_figma_design × N)
  🎨 Figma canvas          ← editable frames, 1920×1080
```

Each slide is a real webpage — styled with CSS, using Google Fonts, full design system.
`generate_figma_design` captures each page and converts it to an **editable Figma frame**.

---

## Prerequisites

1. **Figma desktop app** (browser version won't work)

2. **Enable Dev Mode MCP** in Figma:
   Figma → Preferences → ✅ Dev Mode MCP Server

3. **Connect to Claude Code** (run once):
   ```bash
   claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse
   ```

4. **Install this skill** in Claude Code:
   ```bash
   claude plugin install https://github.com/your-username/figma-ppt-plugin
   ```

5. **Python 3.8+** (for the build script)

---

## Usage

### Generate a presentation

```
/figma-ppt
```

Claude will ask 5 questions in one message, then:
1. Proposes a slide plan (type + headline per slide)
2. You approve or request changes
3. Claude builds the HTML website locally
4. Claude captures each slide into Figma via `generate_figma_design`
5. Editable frames appear on your Figma canvas

### Extract your brand style first (optional)

If you have an existing Figma design file:

```
/figma-ppt:extract-style https://www.figma.com/design/YOUR_FILE_ID/...
```

This creates `./style-guide.json` and uses your exact brand colors, fonts, and aesthetic direction in the slides.

---

## Slide Types

| Type | Web Analogy | Description |
|------|-------------|-------------|
| `HERO` | Landing hero | Opening slide — title, subtitle, author |
| `AGENDA` | Table of contents | Numbered agenda items |
| `CONTENT` | Article section | Heading + bullets + optional image area |
| `TWO_COL` | Feature comparison | Two-column cards for side-by-side content |
| `STATS` | KPI dashboard | 2–4 cards with big numbers, trends, labels |
| `QUOTE` | Full-page testimonial | Full-bleed quote with attribution |
| `DIVIDER` | Chapter break | Section separator with large number watermark |
| `CLOSING` | Footer / CTA | Thank you, key takeaways, contact info |

---

## Aesthetic Directions

Each direction is treated as a **web design system** applied across all slides:

| Direction | Concept | Best for |
|-----------|---------|----------|
| `minimal` | Vast whitespace, single accent, perfect spacing | Executive decks, investor pitches |
| `bold` | Full-bleed color blocks, oversized type | Product launches, all-hands |
| `luxury` | Dark palette, gold/cream, refined typography | Premium brand, board presentations |
| `editorial` | Magazine layouts, typography as design | Creative agencies, storytelling |
| `technical` | Data-dense, monospace, engineering aesthetic | Engineering reviews, data science |
| `playful` | Rounded, bright, energetic | Customer-facing, education |

---

## Project Structure

```
figma-ppt-plugin/
├── .claude-plugin/
│   └── plugin.json                ← Skill manifest
│
├── skills/
│   ├── extract-style/
│   │   ├── SKILL.md               ← Style extraction from Figma MCP
│   │   └── references/
│   │       └── figma-token-guide.md
│   │
│   └── figma-ppt/
│       ├── SKILL.md               ← Main skill: content → HTML → Figma
│       ├── references/
│       │   ├── slide-types.md     ← 8 slide type definitions
│       │   ├── web-design-guidelines.md ← Aesthetic directions
│       │   └── tone-guide.md      ← Tone → aesthetic + density rules
│       └── scripts/
│           ├── build-slides.py    ← HTML/CSS website generator
│           └── serve-and-capture.py ← Local server + capture helper
│
├── schemas/
│   └── style-guide.schema.json
│
├── examples/
│   ├── style-guide-example.json
│   └── slides-plan-example.json
│
└── README.md
```

---

## Tips

- **No style-guide.json?** No problem — the skill uses a clean built-in default palette.
- **Korean presentations?** Use `Pretendard` as display font — it covers all Korean + Latin weights.
- **Fonts missing in Figma?** Install from [fonts.google.com](https://fonts.google.com) — frames are editable so you can swap fonts.
- **Re-run anytime** — each run creates a fresh `slide-output/` folder.
- **Slides are 1920×1080** (Full HD 16:9) — perfect for Figma Prototype mode and PDF export.

---

## License

MIT
