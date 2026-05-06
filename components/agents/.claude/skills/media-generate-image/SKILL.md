---
name: media-generate-image
description: Generate images using Google Gemini via Chrome automation. Use when users request image generation with queries like "generate an image of [description]", "create a picture showing [scene]", or "make an AI image of [subject]". Automatically enriches vague descriptions through interactive dialogue. Returns downloadable image files.
---

# Gemini Image Generation Skill

## Overview

This skill generates images using Google Gemini through Chrome automation. The key differentiator is **smart prompt enhancement**: vague or incomplete image requests are automatically enriched through an interactive dialogue that ensures all critical dimensions are covered (art style, scene elements, mood, perspective, context, narrative).

Users can request image generation with minimal detail, and the skill guides them to complete, well-formed prompts that yield high-quality results.

## Quick Start

**Before (vague request):**
> "generate an image of a cat"

**After (enhanced):**
> "Photorealistic portrait of a fluffy orange tabby cat sitting on a sunlit windowsill, cozy home interior with soft curtains, peaceful and content mood, eye-level medium shot with shallow depth of field, natural morning light, intimate domestic moment"

**Result:** High-quality, well-composed image that matches user intent with professional-level detail.

## Execution Workflow

### Phase 1: Description Assessment

Evaluate the user's request for completeness. A **complete description** includes 4 or more of these dimensions:

1. **Art style** - photorealistic, 3D animated, watercolor, digital art, etc.
2. **Scene elements** - subjects, objects, foreground/background details
3. **Setting/environment** - location, time of day, weather conditions
4. **Mood/atmosphere** - emotions, feeling, tone, energy
5. **Technical details** - camera angle, lighting, composition, lens
6. **Context/narrative** - what's happening, story, purpose

**Decision tree:**
- If missing 3+ dimensions → Trigger Phase 2 (Smart Description Handling)
- If complete (4+ dimensions present) → Skip to Phase 3 (Tool Loading)

### Phase 2: Smart Description Handling

Two-tier approach for enriching incomplete descriptions.

#### Tier 1: Quick Picks (Default)

Present 4 options via AskUserQuestion:

**Options 1-3: Fully-formed interpretations**
Each option provides a complete description with all 6 dimensions filled:

- **Option 1: Photorealistic interpretation**
  - Full description with photographic realism, realistic lighting, detailed textures
  - Example: "Photorealistic image of [subject] with [setting], [mood] atmosphere, [technical details], [context]"

- **Option 2: 3D Animated interpretation**
  - Full description in Pixar/Disney style, smooth rendering, vibrant colors
  - Example: "Modern 3D animated [subject] in [style] with [setting], [mood] feeling, [technical details], [context]"

- **Option 3: Artistic/Traditional medium interpretation**
  - Full description using painting/illustration styles
  - Example: "Watercolor painting of [subject] showing [elements], [setting], [mood] atmosphere, [technical details], [context]"

- **Option 4: "Build the description step-by-step through dialogue"**
  - Triggers Tier 2 dialogue mode

#### Tier 2: Dialogue Mode (If Option 4 selected)

Conduct 4 sequential AskUserQuestion calls to build complete description:

**Question 1: Art Style**
- Photorealistic (lifelike, detailed, camera-captured quality)
- 3D Animated (Pixar/Disney style, smooth rendering, vibrant)
- Digital Art (illustrated, painterly, artistic interpretation)
- Traditional Medium (watercolor, oil painting, pencil sketch)

**Question 2: Camera Perspective**
- Eye-level medium shot (natural, conversational perspective)
- Low angle looking up (dramatic, heroic, powerful)
- High angle bird's eye view (overview, contextual, expansive)
- Close-up detail shot (intimate, focused, revealing)

**Question 3: Scene Elements**
- Minimal/clean (subject only, simple background, uncluttered)
- Detailed environment (rich setting, many objects, complex)
- Natural setting (outdoor, organic elements, landscape)
- Indoor/architectural (interior space, man-made structures)

**Question 4: Mood/Atmosphere**
- Bright and cheerful (happy, energetic, vibrant, uplifting)
- Calm and serene (peaceful, tranquil, soft, relaxing)
- Dramatic and moody (intense, cinematic, contrasting, powerful)
- Mysterious and ethereal (dreamy, magical, atmospheric, enigmatic)

**Combine all selections** with original user request to form complete description.

### Phase 3: Tool Loading

Load Chrome automation tools once per session:

```python
ToolSearch(query="claude-in-chrome", max_results=5)
```

This loads all `mcp__claude-in-chrome__*` tools at once.

**Skip this step** if tools are already loaded in the current session.

### Phase 4: Chrome Session Setup

**Step 1: Get or create tab context**

```python
mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty=true)
```

Returns `tabId` for subsequent operations.

**Step 2: Navigate to Gemini**

```python
mcp__claude-in-chrome__navigate(
    tabId=[from Step 1],
    url="https://gemini.google.com/app"
)
```

**Wait 3 seconds** for page to fully load before proceeding.

### Phase 5: Image Generation

**Step 1: Enter prompt into Gemini input box**

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=[from Phase 4],
    text="""
        const editor = document.querySelector('[role="textbox"]');
        if (editor) {
            editor.textContent = "Create an image: [FULL_DESCRIPTION]";
            editor.dispatchEvent(new Event('input', { bubbles: true }));
            "Prompt entered successfully";
        } else {
            "Error: Editor not found";
        }
    """
)
```

**CRITICAL DETAILS:**
- Parameter name is `text` (NOT `code` or `script`)
- Use `[role="textbox"]` selector for contenteditable div
- Set `textContent` (NOT `value` property - that's for input elements)
- Dispatch `input` event to trigger Gemini's text detection
- Prepend "Create an image: " to the description

**Step 2: Click send button**

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=[from Phase 4],
    text="""
        const sendBtn = document.querySelector('button[aria-label*="Send"]') ||
                       document.querySelector('button[type="submit"]');
        if (sendBtn) {
            sendBtn.click();
            "Request sent successfully";
        } else {
            "Error: Send button not found";
        }
    """
)
```

**Step 3: Wait for image generation**

Poll every 5 seconds for up to 30 seconds:

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=[from Phase 4],
    text="""
        const images = document.querySelectorAll('img[src*="googleusercontent"]');
        images.length > 0 ? "Ready" : "Generating...";
    """
)
```

**Step 4: Download generated image**

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=[from Phase 4],
    text="""
        const dlBtn = document.querySelector('button[aria-label*="Download"]') ||
                      Array.from(document.querySelectorAll('button')).find(b =>
                          b.getAttribute('aria-label')?.toLowerCase().includes('download') ||
                          b.textContent.toLowerCase().includes('download')
                      );
        if (dlBtn) {
            dlBtn.click();
            "Image downloaded";
        } else {
            "Download button not found";
        }
    """
)
```

**Step 5: Close tab to terminate session**

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=[from Phase 4],
    text="window.close(); 'Tab closed'"
)
```

This cleans up the browser session after the image is downloaded.

### Phase 6: Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Editor not found" | Page not fully loaded | Wait 3 more seconds, retry |
| "Send button not found" | Button selector changed | Try alternative selectors (see patterns) |
| "No image after 30s" | Generation timeout | Notify user to check tab manually |
| Wrong parameter error | Used "code" instead of "text" | Use "text" parameter for javascript_tool |
| TypeError on textContent | Tried .value on div | Use textContent for contenteditable divs |
| Tools not loaded | Skipped ToolSearch | Call ToolSearch with "claude-in-chrome" |

**Error Prevention Checklist:**
- [ ] ToolSearch called to load Chrome tools
- [ ] tabs_context_mcp returns valid tabId
- [ ] javascript_tool uses "text" parameter (not "code")
- [ ] Contenteditable div uses textContent (not value)
- [ ] Wait 3 seconds after navigation
- [ ] Element existence checked before manipulation
- [ ] Image downloaded before closing tab
- [ ] Tab closed to terminate session
- [ ] Polling timeout doesn't exceed 30 seconds

### Phase 7: Output Formatting

Return to user:

```markdown
Image generated successfully.

**Prompt used:** [full description]
**Saved to:** ~/Downloads/ (check your Downloads folder)
**Session:** Closed

The image has been downloaded and the browser tab has been closed.
```

## Token Optimization Rules

1. **No preamble** - Start directly with description assessment
2. **Load tools once** - ToolSearch once per session, reuse tools
3. **Reuse tab context** - Don't create new tabs for each generation
4. **Batch JavaScript operations** - Combine checks where possible
5. **Direct downloads** - Download image and close tab, no screenshots needed
6. **Single description expansion** - Don't regenerate or re-explain prompt

## References

For implementation details, see:
- [Chrome Automation Patterns](references/chrome-automation-patterns.md) - JavaScript snippets, selectors, error handling
- [Description Templates](references/description-templates.md) - Example complete descriptions by category

## Common Issues & Solutions

**Issue: Tab not responding**
- Solution: Check if user has closed the tab. Call tabs_context_mcp to get fresh context.

**Issue: Image quality doesn't match expectations**
- Solution: Description may still be too vague. Review the 6 dimensions and ensure each is explicitly specified.

**Issue: Gemini returns text instead of image**
- Solution: Ensure prompt starts with "Create an image:" or "Generate an image:"

**Issue: Download fails**
- Solution: Check if download button selector has changed. Try alternative selectors or notify user to download manually from the tab before closing.

---

**For other media generation tasks**, check related skills if any are added in future.
