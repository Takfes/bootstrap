---
name: presentation-builder
description: Build a complete, professional presentation from scratch — narrative planning, slide outlining, visual design, and PPTX generation. Use this skill whenever the user wants to create a slide deck, pitch, report, keynote, or any structured presentation, especially when they have raw material (notes, data, a brief, research) that needs to be shaped into an audience-ready story. Trigger on: "build me a deck", "create a presentation", "I need slides for X", "turn this into a presentation", "make me a pitch deck", "put together a deck", or any variation of creating slides or a deck.
---

# Presentation Builder

Transform raw material — briefs, notes, data, research — into audience-ready presentations with a strong narrative spine and world-class visual design.

The workflow has five phases. Do not skip or reorder them. Each phase gates the next.

---

## Phase 1 — Understand the Ask

Before touching content, collect five things in a single message:

1. **Goal** — What should the audience walk away knowing, feeling, or doing?
2. **Audience** — Who are they? What's their familiarity with the subject? What do they care about?
3. **Tone / Style** — Formal, energetic, technical, financial, pitch? Or pick from the five brand styles (see `references/design-system.md`).
4. **Target slide count** — A rough range is fine. Rule of thumb: 1 slide per minute of speaking time.
5. **Source material** — Paste content, describe what exists, or share files now.

Do not proceed to Phase 2 until all five are confirmed. If the user's initial message already answers some, ask only for what's missing.

---

## Phase 2 — Content Synthesis

Act as an information architect and narrative designer. Read all provided material and:

1. **Identify what matters** — What are the key themes, insights, and tensions in the material? What should the audience understand that they don't yet?
2. **Define the key messages** — What are the 3–5 things this deck must communicate? Rank them by importance.
3. **Design the narrative arc** — What story does the deck tell, from slide 1 to the last? What's the opening hook? What's the resolution? What does the audience feel at each stage?
4. **Assign a "so what" to each proposed slide** — Every slide must have a clear purpose in the flow. If you can't state the purpose in one sentence, the slide doesn't belong or needs to be merged.
5. **Separate slide content from voice** — For each slide, determine: what goes on the slide (the minimum needed to anchor attention) vs. what the presenter says aloud. Dense slides kill presentations.

At the end of Phase 2, offer speaker notes: *"Do you want speaker notes included — one paragraph per slide with the voiceover talking points?"* Generate them only if the user answers yes.

---

## Phase 3 — Plan the Deck (Gate)

Produce a `slide-outline.md` file. Format each slide as a numbered block:

```
## Slide N — [Title]
- Key message: [one sentence — the "so what"]
- On-slide content: [what appears on the slide]
- Visual / data needed: [chart, image, icon, metric, diagram — be specific]
- Speaker note: [voiceover talking point — only if requested in Phase 2]
```

**Hard gate: do not generate any slides until the outline is explicitly approved.**

After sharing the outline:
- Flag any slides that seem redundant, missing, or out of order
- Invite the user to add, remove, reorder, or rewrite any entry
- Wait for explicit approval ("looks good", "proceed", etc.) before moving on

Save the approved outline to `slide-outline.md` in the working directory.

---

## Phase 4 — Build Slides

### 4a — Select Brand Style

If the user specified a style in Phase 1, confirm it. Otherwise, recommend one based on audience and tone:

| Audience / Tone | Recommended Style |
|---|---|
| Product, tech, launch | Tech Keynote |
| Enterprise, B2B, corporate | Corporate Professional |
| Marketing, creative, consumer | Creative Bold |
| Finance, investment, board | Financial Elite |
| Fundraising, accelerator, demo day | Startup Pitch |

Full brand specs (colors, typography, spacing, effects) are in `references/design-system.md`.

### 4b — Map Outline to Slide Templates

For each outline entry, assign a slide template:

| Content type | Template |
|---|---|
| Opening / deck title | title_slide |
| New section / chapter | chapter_intro |
| 1–3 key points | key_metrics_dashboard |
| Problem vs solution | before_after_comparison |
| Process / steps | process_flow |
| Timeline / roadmap | timeline_slide |
| Team | team_introduction |
| Data table | data_table_slide |
| Chart / trend | chart_comparison |
| Two columns | two_column_text |
| Full image | full_image_slide |
| Quote / testimonial | quote_testimonial |
| Closing / CTA | thank_you_slide |

### 4c — Assign a Visual Component to Every Slide

Every slide must have a visual component. Text-only slides are not allowed. Choose from:

- **Card Grid** — 2–4 cards with icon, title, one-liner. For features, benefits, categories.
- **Comparison Panel** — Two columns with vs divider. For before/after, option A vs B.
- **Stat Callout** — One large number or percentage with label. For key metrics.
- **Step Flow** — Numbered steps with arrows. For processes, tutorials, how-it-works.
- **Quote Block** — Large quotation marks, italic text, attribution. For testimonials, key statements.
- **Icon + Label List** — Emoji/icon left, label right. For feature lists, agendas, checklists.
- **Code Block** — Monospace on dark card. For code, config, command line.
- **Timeline** — Horizontal line with dots and labels. For roadmaps, history, phases.
- **Metric Dashboard** — 3–4 stat boxes in a row. For KPIs, performance comparisons.
- **Full-Bleed Image** — Immersive visual with overlay if text is needed.

Content rules:
- One idea per slide. Two points → two slides.
- Max ~30 words visible on the slide itself.
- No bullet dumps. Use Icon + Label List if you need a list.
- Big text over small text. Whitespace is structure.

### 4d — Generate Output

**HTML preview (optional):** Ask the user: *"Do you want an HTML preview to review the deck in a browser before the PPTX is exported?"* Generate only if they say yes. Produce a self-contained HTML file with fullscreen slides, keyboard navigation, and the visual components above. Use the brand style's color palette and typography scale.

**PPTX (primary output):** Invoke the `document-skills:pptx` skill for all PPTX creation and editing. That skill owns the technical execution — pptxgenjs for creation from scratch, the unpack/edit/pack workflow for templates, and the QA + visual verification loop. This skill owns the narrative, structure, and design decisions; `document-skills:pptx` handles the file generation.

When handing off to `document-skills:pptx`, provide:
- The approved slide outline (from Phase 3)
- The selected brand style specs from `references/design-system.md` (colors, fonts, spacing)
- The visual component assigned to each slide
- Whether speaker notes should be included

Apply the full design system:
- Typography hierarchy (hero title 72–96pt → caption 18–20pt)
- Spacing system (gutters, margins, padding from brand style)
- Color palette from brand style
- Subtle shadow on text boxes (distance 2, angle 135, blur 4, transparency 60%)
- Gradient overlay on images at 20% opacity if text overlays them

---

## Phase 5 — Polish & Validate

### Transitions & Animations
Apply per brand style (see `references/animation-guide.md`):
- Max 1–2 transition types per deck
- Entrance animations: Fade In for text (0.4s), Wipe From Bottom for images (0.6s)
- Emphasis: Pulse once on the single most important metric — nowhere else
- Tier 3 transitions (Ferris Wheel, Curtains, Origami, Page Curl, Dissolve): never

### Consistency Check
- Font families: max 2 per deck
- Colors: only from the brand palette
- Margins and gutters: consistent throughout
- Alignment: everything snaps to grid
- Image resolution: minimum 1920×1080

### Quality Checklist

**Visual consistency**
- [ ] All slides use brand palette (no random colors)
- [ ] Typography follows hierarchy (max 4 font sizes)
- [ ] Spacing consistent (same margins throughout)
- [ ] Alignment precise (grid-snapped)

**Content clarity**
- [ ] One main idea per slide
- [ ] Slide titles are clear and outcome-oriented
- [ ] No walls of text (max 6 lines body text)
- [ ] Every slide has a visual component

**Motion & polish**
- [ ] 1–2 transition types only
- [ ] Animation duration feels natural (0.3–0.8s)
- [ ] No distracting motion (passes boardroom test)
- [ ] Emphasis animation on one slide only

**Brand alignment**
- [ ] Colors match brand style
- [ ] Typography matches brand style
- [ ] Layout follows brand conventions
- [ ] Deck feels cohesive start to finish

---

## Reference Files

Load when needed — do not pre-load all:

- `references/design-system.md` — full brand style specs, typography, spacing, color rules
- `references/visual-components.md` — detailed component specs with HTML/CSS patterns
- `references/animation-guide.md` — transition tier system, per-brand animation strategy, timing standards

---

## Requirements

**PPTX generation:**
```bash
pip install python-pptx pillow pyyaml
# Or via MCP: npx @smithery/cli install @gongrzhe/office-powerpoint-mcp-server
```

**Content analysis script:**
```bash
python scripts/analyze_content.py input.md
```
