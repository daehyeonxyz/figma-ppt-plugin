---
name: figma-ppt
description: Generate a production-grade Figma presentation by building a real 1920×1080 HTML/CSS website and capturing each slide into editable Figma frames via the Figma Dev Mode MCP. Use for "make a presentation", "create slides", "build a deck", "generate Figma presentation", "슬라이드 만들어줘", "프레젠테이션 생성".
allowed-tools: Read, Write, Bash, mcp__b2ee9eae-c125-457f-bf25-a85d11b3e1a2__get_design_context, mcp__b2ee9eae-c125-457f-bf25-a85d11b3e1a2__get_variable_defs, mcp__b2ee9eae-c125-457f-bf25-a85d11b3e1a2__get_metadata, mcp__b2ee9eae-c125-457f-bf25-a85d11b3e1a2__generate_diagram
---

# figma-ppt Skill

Generate a Figma presentation by thinking like a **frontend developer building a 1920×1080 website**.

**Pipeline:**
1. Collect content + tone from user
2. Build a multi-page HTML/CSS slide website (each slide = 1 full page)
3. Serve it locally via Python HTTP server
4. Call `generate_figma_design` for each slide URL → editable Figma frames

**Prerequisites (user must have):**
- Figma desktop app (not browser)
- Dev Mode MCP enabled: Figma → Preferences → "Dev Mode MCP Server" ON
- MCP connected: `claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse`

---

## Phase 1: Style Loading (Optional)

Check if `./style-guide.json` exists in the current working directory.

**If it exists**: Read it and extract `colors`, `typography`, `aesthetic.direction`.
Use these as CSS custom properties for the HTML slides.

**If it does NOT exist**: Silently use the built-in defaults (clean dark palette, Inter font).
Do NOT ask the user about this — just proceed.

---

## Phase 2: Content Collection

Ask the user ALL of these in a **single message**:

```
Let's build your Figma presentation. Please answer:

1. Title and purpose — what is this presentation about and why?
2. Audience — executives / engineers / customers / students / general
3. Tone & mood — choose one or describe your own:
   - minimal  (clean, vast whitespace, single accent)
   - bold     (high contrast, oversized type, color-first)
   - luxury   (dark + gold/cream, premium feel)
   - editorial (magazine layout, typography-driven)
   - technical (data-dense, monospace, engineering aesthetic)
   - playful  (rounded, friendly, energetic)
4. Content — paste your outline, bullet points, data, or key messages.
   (More detail = better slides. Raw notes are fine.)
5. Slide count — how many? Or type "auto" for me to decide.
```

Wait for the full response before proceeding.

---

## Phase 3: Aesthetic Direction + Slide Planning

### 3A. Choose Aesthetic Direction

Based on the tone, commit to ONE direction from `references/web-design-guidelines.md`.

**Critical rules (never break these):**
- Choose an EXTREME, not a middle ground
- NEVER: Inter Regular on white with purple gradient
- NEVER: centered everything with equal visual weight
- Each presentation must feel specifically designed for its topic and audience

Announce to user (briefly):
```
Aesthetic: [DIRECTION] — [1-sentence visual concept]
Palette: [primary color] + [background] + [accent]
Font: [font choice]
```

### 3B. Map Content to Slide Types

Reference `references/slide-types.md` for 8 types: HERO, AGENDA, CONTENT, TWO_COL, STATS, QUOTE, DIVIDER, CLOSING
Reference `references/tone-guide.md` for density and count rules.

Rules:
- Always start with HERO, always end with CLOSING
- Add AGENDA if 4+ content sections
- Use DIVIDER between major sections (6+ slides)
- Use QUOTE for inspirational/formal tone if a strong quote exists

### 3C. Show Slide Plan + Get Approval

```
Presentation: "[TITLE]" ([N] slides)
Aesthetic: [DIRECTION] | Tone: [TONE] | Audience: [AUDIENCE]

 1. [HERO]     — "Title"
 2. [AGENDA]   — sections overview
 3. [CONTENT]  — "Key Point 1"
 ...

Say "yes" or "go" to start building. Or request changes.
```

Wait for approval before Phase 4.

---

## Phase 4: Build HTML Slide Website

After approval, build the slide website using the script:

### Step 4A: Write slides-plan.json

Write `./slides-plan.json` with the full slide structure:
```json
{
  "title": "Presentation Title",
  "aesthetic": "bold",
  "palette": {
    "primary": "#0050FF",
    "background": "#0A0A0A",
    "surface": "#111111",
    "accent": "#FF3B00",
    "textPrimary": "#FFFFFF",
    "textSecondary": "#888888"
  },
  "fonts": {
    "display": "Space Grotesk",
    "body": "Space Grotesk"
  },
  "slides": [
    {
      "type": "HERO",
      "content": {
        "title": "...",
        "subtitle": "...",
        "author": "...",
        "date": "..."
      }
    }
  ]
}
```

### Step 4B: Run the HTML builder

```bash
python skills/figma-ppt/scripts/build-slides.py \
  --slides-plan ./slides-plan.json \
  --output-dir ./slide-output
```

This creates:
```
slide-output/
  index.html          ← slide navigation page
  slides/
    01-hero.html
    02-agenda.html
    03-content.html
    ...
  assets/
    styles.css
```

### Step 4C: Verify the output

```bash
python -m http.server 7890 --directory ./slide-output &
```

Check that `http://localhost:7890/slides/01-hero.html` loads correctly.

---

## Phase 5: Capture to Figma via generate_figma_design

For each slide in order, call the Figma MCP to capture it as an editable frame.

**IMPORTANT**: Call `generate_figma_design` for each slide URL in sequence.
Wait for each call to complete before proceeding to the next.

The tool will:
1. Open the URL in a browser
2. Capture the rendered 1920×1080 page
3. Convert it to an editable Figma frame on the canvas

After all slides are captured, kill the local server:
```bash
kill $(lsof -t -i:7890) 2>/dev/null || true
```

---

## Phase 6: Report Results

```
✅ Your presentation is now in Figma!

[N] editable frames have been created on your canvas.

SLIDES CREATED:
  1. HERO     — "[Title]"
  2. AGENDA   — "[Agenda heading]"
  ...

NEXT STEPS IN FIGMA:
  • Select all frames → Cmd/Ctrl+Shift+H to zoom fit
  • Use Prototype mode (F key) to present
  • Frames are fully editable — text, colors, shapes

FONTS USED: [font names]
If fonts appear substituted, install them from fonts.google.com
```

---

## Reference Files

- [references/slide-types.md](references/slide-types.md) — 8 slide types with content fields
- [references/web-design-guidelines.md](references/web-design-guidelines.md) — Aesthetic directions, layout, anti-patterns
- [references/tone-guide.md](references/tone-guide.md) — Tone → aesthetic + slide count mappings
