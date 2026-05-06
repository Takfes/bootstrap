# Design System Reference

Full brand style specs, typography hierarchy, spacing, and color rules. Load this file when building slides in Phase 4.

---

## 5 Brand Styles

### 1. Tech Keynote — Apple / Tesla
- **Colors**: Black `#000000`, White `#FFFFFF`, Accent Blue `#0071E3`, Secondary text `#8E8E93`
- **Fonts**: SF Pro Display (title), SF Pro Text (body) — fallbacks: Helvetica Neue / Helvetica
- **Title size**: 72pt; Subtitle: 44pt; Body: 32pt; Caption: 20pt
- **Spacing**: Gutter 120px, Title margin 80px, Section spacing 60px, Paragraph 32px, Element padding 30px
- **Layout**: Center-aligned, maximum whitespace, single focal point per slide
- **Transitions**: Push (0.4s), Fade (0.6s) — max 2 animations per slide
- **Effects**: Subtle shadows, no gradients, minimal overlays
- **Use for**: Product launches, tech demos, keynotes

### 2. Corporate Professional — Microsoft / IBM
- **Colors**: Navy `#003366`, Steel Blue `#0078D4`, Warm Gray `#F3F2F1`, Text `#323130` / `#605E5C`
- **Fonts**: Segoe UI — fallback: Arial
- **Title size**: 64pt; Subtitle: 36pt; Body: 28pt; Caption: 18pt
- **Spacing**: Gutter 100px, Title margin 60px, Section spacing 48px, Paragraph 28px, Element padding 24px
- **Layout**: Left-aligned, balanced grid, data-friendly
- **Transitions**: Morph (0.8s), Fade (0.8s) — max 3 animations per slide
- **Effects**: Moderate shadows, subtle gradients, professional overlays
- **Use for**: Business reports, proposals, enterprise decks

### 3. Creative Bold — Google / Airbnb
- **Colors**: Red `#EA4335`, Blue `#4285F4`, Yellow `#FBBC05`, Text `#202124` / `#5F6368`
- **Fonts**: Product Sans / Montserrat (title), Google Sans / Open Sans (body)
- **Title size**: 76pt; Subtitle: 40pt; Body: 30pt; Caption: 20pt
- **Spacing**: Gutter 80px, Title margin 64px, Section spacing 52px, Paragraph 30px, Element padding 28px
- **Layout**: Dynamic, asymmetric, playful whitespace
- **Transitions**: Zoom (0.5s), Reveal (0.6s), Push (0.4s) — max 4 animations per slide
- **Effects**: Bold shadows, vibrant gradients, creative overlays
- **Use for**: Marketing, design showcases, consumer presentations

### 4. Financial Elite — Goldman Sachs / McKinsey
- **Colors**: Charcoal `#2C3E50`, Gold `#D4AF37`, White `#FFFFFF`, Secondary text `#7F8C8D`
- **Fonts**: Garamond — fallback: Georgia (serif throughout)
- **Title size**: 60pt; Subtitle: 36pt; Body: 26pt; Caption: 18pt
- **Spacing**: Gutter 110px, Title margin 70px, Section spacing 50px, Paragraph 26px, Element padding 26px
- **Layout**: Center-aligned, traditional hierarchy, balanced
- **Transitions**: Fade only (0.4s) — max 1 animation per slide
- **Effects**: Minimal shadows, no gradients, sophisticated overlays
- **Use for**: Investor decks, financial reports, board presentations

### 5. Startup Pitch — Y Combinator / 500 Startups
- **Colors**: Black `#000000`, Indigo `#6366F1`, White `#FFFFFF`, Text `#111827` / `#6B7280`
- **Fonts**: Inter — fallback: Roboto
- **Title size**: 68pt; Subtitle: 38pt; Body: 28pt; Caption: 18pt
- **Spacing**: Gutter 90px, Title margin 56px, Section spacing 44px, Paragraph 26px, Element padding 22px
- **Layout**: Left-aligned, efficient whitespace, metric-driven focal points
- **Transitions**: Push (0.3s), Fade (0.3s) — max 2 animations per slide
- **Effects**: Sharp shadows, accent gradients, data-focused overlays
- **Use for**: Fundraising, accelerator demos, investor pitches

---

## Typography Hierarchy

| Level | Size range | Weight | Line height | Use |
|---|---|---|---|---|
| Hero title | 72–96pt | Bold | 1.1× | Deck title, cover |
| Section title | 54–72pt | Semibold | 1.2× | Chapter intro |
| Slide title | 44–54pt | Semibold | 1.3× | Every content slide |
| Body large | 32–36pt | Regular | 1.4× | Primary body text |
| Body | 24–28pt | Regular | 1.5× | Secondary text |
| Caption | 18–20pt | Light | 1.6× | Labels, footnotes |

**Rules:**
- Max 2 font families per deck
- Max 4 font sizes per deck
- Title max 2 lines
- Body max 6 lines
- Bullet max 5 items

---

## Spacing System

| Element | Value |
|---|---|
| Min margin from slide edge | 80px |
| Title → content gap | 60px |
| Between elements | 40px |
| Bullet spacing | 24px |

Brand-specific gutter and padding override these defaults — see brand spec above.

---

## Color Application Rules

| Role | Usage |
|---|---|
| Background | Brand background — high contrast with all text |
| Primary | Titles, key elements, CTAs |
| Secondary | Subtitles, secondary text |
| Accent | Highlights, data points, emphasis only |
| Text | 95% opacity for readability |

- Max 4 colors per slide
- Minimum contrast ratio for text: 4.5:1
- Accent color: highlights, CTAs, data points — never backgrounds

---

## Image Guidelines

- Minimum resolution: 1920×1080
- Preferred: 3840×2160 (4K)
- Aspect ratio: 16:9
- Text overlay: apply gradient overlay at 20% opacity
- Image quality: >85% compression

---

## Visual Effects

**Text boxes:**
```
shadow: distance 2px, angle 135°, blur 4px, transparency 60%
```

**Images with text overlay:**
```
gradient overlay: linear, opacity 20%
```
