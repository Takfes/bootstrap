# Visual Components Reference

Every slide must have at least one visual component. Text-only slides are not allowed.

---

## Component Menu

### Card Grid
2–4 cards in a row, each with an icon or emoji, a bold title, and a one-line description.
- **Use for**: Features, benefits, categories, options
- **Avoid**: More than 4 cards — split into two slides

```
[🔒 Security]     [⚡ Speed]       [📊 Analytics]
Title here        Title here       Title here
One-line desc.    One-line desc.   One-line desc.
```

---

### Comparison Panel
Two columns side by side, optionally with a vs divider. Contrasting background tones (muted left, vivid right works well for before/after).
- **Use for**: Before/after, old vs new, option A vs B, problem vs solution
- **Avoid**: More than 3 rows per column — it becomes a wall

---

### Stat Callout
One large number or percentage (60–96pt, accent color) with a short label below (18–20pt, secondary text).
- **Use for**: Key metrics, growth numbers, single impressive data points
- **Avoid**: Showing more than one stat per callout — use Metric Dashboard for multiples

---

### Step Flow
Numbered steps with arrows between them (horizontal or vertical). Each step has a number, a short label, and optionally a one-line description.
- **Use for**: Processes, tutorials, how-it-works sequences, workflows
- **Avoid**: More than 5 steps — split or summarise

---

### Quote Block
Large decorative quotation marks, italic text at 28–36pt, attribution below at 18pt.
- **Use for**: Testimonials, expert quotes, key statements, pull quotes
- **Avoid**: Quotes longer than 3 lines — truncate and paraphrase

---

### Icon + Label List
Vertical list with an emoji or icon on the left and a bold label + short description on the right. Better than bullet points — visually anchors each item.
- **Use for**: Feature lists, agendas, checklists, capability overviews
- **Avoid**: More than 5 items — the slide becomes a document

---

### Code Block
Monospace font on a dark card with syntax-style coloring. Language label top-right.
- **Use for**: Code examples, command-line instructions, config files, API samples
- **Avoid**: More than 15–20 lines — excerpt the critical part

---

### Timeline
Horizontal line with labeled dots above and below. Each dot = a phase, date, or milestone.
- **Use for**: Roadmaps, project phases, company history, event sequence
- **Avoid**: More than 6 points — the dots compress and lose readability

---

### Metric Dashboard
3–4 stat boxes in a row, each with a label and value. Good for KPI overviews.
- **Use for**: Performance data, KPI summaries, comparisons across dimensions
- **Avoid**: More than 4 boxes — use a table instead

---

### Full-Bleed Image
Image fills the slide (or one full half). If text overlays, apply a 20% gradient overlay for contrast.
- **Use for**: Scene-setting opening, product photography, location, emotional impact
- **Avoid**: Low-resolution images — minimum 1920×1080

---

## Slide Content Rules

1. **One idea per slide.** Two distinct points → two slides.
2. **Max ~30 words visible on the slide.** The rest belongs in speaker notes.
3. **No bullet dumps.** Convert to Icon + Label List if you need a list.
4. **Big text over small text.** When in doubt, make it bigger.
5. **Whitespace is structure.** Crowded slides lose the audience.
6. **Every slide has a visual component.** No exceptions.

---

## Component-to-Template Mapping

| Component | Best slide template |
|---|---|
| Card Grid | key_metrics_dashboard, three_column_layout |
| Comparison Panel | before_after_comparison, chart_comparison |
| Stat Callout | key_metrics_dashboard (single metric) |
| Step Flow | process_flow, timeline_slide |
| Quote Block | quote_testimonial |
| Icon + Label List | two_column_text, bullet_hierarchy_slide |
| Code Block | two_column_text (code right, explanation left) |
| Timeline | timeline_slide |
| Metric Dashboard | key_metrics_dashboard |
| Full-Bleed Image | full_image_slide |
