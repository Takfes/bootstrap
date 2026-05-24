# Chrome Automation Patterns for Gemini Image Generation

This document contains reusable JavaScript patterns and best practices for automating Google Gemini image generation through Chrome.

## Tool Loading Pattern

Load all Chrome automation tools once per session:

```python
# Load all mcp__claude-in-chrome__* tools at once
ToolSearch(query="claude-in-chrome", max_results=5)

# Returns tools including:
# - mcp__claude-in-chrome__tabs_context_mcp
# - mcp__claude-in-chrome__navigate
# - mcp__claude-in-chrome__javascript_tool
# - mcp__claude-in-chrome__computer
# - And others...
```

**Don't** try to load individual tools like "browser_take_screenshot" - they don't exist as standalone tools.

## Tab Context Pattern

Get existing tabs or create new tab group:

```python
# Get or create tab context
result = mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty=true)

# Returns structure like:
# {
#   "availableTabs": [
#     {"id": 12345, "url": "https://...", "title": "..."}
#   ],
#   "tabGroupId": "group-abc123"
# }

# Extract tabId for subsequent operations
tabId = result["availableTabs"][0]["id"]
```

**Reuse tabs** across multiple image generations instead of creating new ones each time.

## Navigation Pattern

Navigate to Gemini and wait for page load:

```python
# Navigate to Gemini
mcp__claude-in-chrome__navigate(
    tabId=12345,
    url="https://gemini.google.com/app"
)

# CRITICAL: Wait 2-3 seconds after navigation
# The page needs time to render DOM elements
import time
time.sleep(3)
```

**Don't** proceed with DOM manipulation immediately after navigation - wait times are critical.

## Contenteditable Manipulation

Gemini uses contenteditable divs, not traditional input fields:

```javascript
// ✅ CORRECT - Use textContent for contenteditable divs
const editor = document.querySelector('[role="textbox"]');
if (editor) {
    editor.textContent = "Create an image: a photorealistic cat on a windowsill";
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    "Prompt entered successfully";
} else {
    "Error: Editor not found";
}

// ❌ WRONG - Don't use .value on contenteditable divs
editor.value = "text";  // This will fail with TypeError

// ❌ WRONG - Don't use innerHTML (can cause XSS issues)
editor.innerHTML = "text";  // Use textContent instead
```

**Key points:**
- Use `textContent` property, not `value`
- Dispatch `input` event to trigger Gemini's text detection
- Always check element exists before manipulation
- Use `[role="textbox"]` selector for maximum reliability

## Button Click Pattern

Find and click buttons with fallback selectors:

```javascript
// Primary selector with fallbacks
const sendBtn = document.querySelector('button[aria-label*="Send"]') ||
                document.querySelector('button[type="submit"]') ||
                Array.from(document.querySelectorAll('button')).find(b =>
                    b.textContent.toLowerCase().includes('send')
                );

if (sendBtn) {
    sendBtn.click();
    "Button clicked successfully";
} else {
    "Error: Send button not found";
}
```

**Why fallbacks matter:**
- Gemini UI can change
- Aria-labels may vary by locale
- Multiple fallback strategies increase reliability

## Polling Pattern

Poll for image generation completion:

```javascript
// Check if image generation is complete
const checkImageReady = () => {
    const images = document.querySelectorAll('img[src*="googleusercontent"]');
    return images.length > 0 ? "Ready" : "Generating...";
};

// Returns "Ready" when image appears, "Generating..." otherwise
```

**Usage:**
```python
# Poll every 5 seconds for up to 30 seconds
max_attempts = 6
for attempt in range(max_attempts):
    result = mcp__claude-in-chrome__javascript_tool(
        action="javascript_exec",
        tabId=12345,
        text="document.querySelectorAll('img[src*=\"googleusercontent\"]').length > 0 ? 'Ready' : 'Generating...'"
    )

    if "Ready" in result:
        break

    if attempt < max_attempts - 1:
        time.sleep(5)
    else:
        # Timeout - notify user
        break
```

## Screenshot Pattern

Capture the generated image:

```python
# Take screenshot of current tab
mcp__claude-in-chrome__computer(
    action="screenshot",
    tabId=12345
)

# Image is automatically saved to ~/Downloads/
```

**Alternative: Download button**

```javascript
// Find and click download button
const dlBtn = document.querySelector('button[aria-label*="Download"]') ||
              Array.from(document.querySelectorAll('button')).find(b =>
                  b.getAttribute('aria-label')?.includes('download') ||
                  b.textContent.toLowerCase().includes('download')
              );

if (dlBtn) {
    dlBtn.click();
    "Download initiated";
} else {
    "Download button not found - use screenshot fallback";
}
```

## Error Handling Pattern

Always check for element existence and return descriptive messages:

```javascript
// Template for safe DOM manipulation
const performAction = () => {
    const element = document.querySelector('selector-here');

    if (!element) {
        return "Error: Element not found";
    }

    try {
        // Perform action
        element.click();
        return "Success: Action completed";
    } catch (error) {
        return `Error: ${error.message}`;
    }
};
```

**Error response format:**
- Success: "Success: [action description]"
- Error: "Error: [specific problem]"
- This makes debugging easier in tool results

## Common Selectors for Gemini

| Element | Primary Selector | Fallback Selectors |
|---------|-----------------|-------------------|
| Input box | `[role="textbox"]` | `[contenteditable="true"]` |
| Send button | `button[aria-label*="Send"]` | `button[type="submit"]`, button containing "send" text |
| Generated images | `img[src*="googleusercontent"]` | `img[src*="gemini"]` |
| Download button | `button[aria-label*="Download"]` | Button containing "download" text |
| Response container | `[data-test-id="conversation"]` | `.conversation-container` |

**Selector tips:**
- Attribute contains (`*=`) is more robust than exact match (`=`)
- Role attributes are more stable than class names
- Test selectors in Chrome DevTools before using in automation

## Wait Times Reference

| Operation | Recommended Wait | Reason |
|-----------|------------------|--------|
| After navigation | 2-3 seconds | DOM rendering and JavaScript initialization |
| Between operations | 1-2 seconds | UI state updates and animations |
| Image generation | 15-30 seconds (poll every 5s) | AI processing time |
| After button click | 1 second | UI response and loading states |

**Don't:**
- Wait longer than necessary (wastes time)
- Skip waits entirely (causes errors)
- Use fixed long waits (use polling instead)

## Parameter Reference

### javascript_tool parameters

```python
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",      # Use "javascript_exec" for code execution
    tabId=12345,                    # Tab ID from tabs_context_mcp
    text="console.log('hello')"     # Use "text" parameter (NOT "code" or "script")
)
```

**Common mistakes:**
- ❌ Using `code=` instead of `text=`
- ❌ Using `script=` instead of `text=`
- ❌ Using action="execute" instead of "javascript_exec"

### computer tool parameters

```python
mcp__claude-in-chrome__computer(
    action="screenshot",    # Use "screenshot" for capturing images
    tabId=12345            # Tab ID from tabs_context_mcp
)
```

## Complete Example Workflow

```python
# 1. Load tools (once per session)
ToolSearch(query="claude-in-chrome", max_results=5)

# 2. Get/create tab
tab_result = mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty=true)
tab_id = tab_result["availableTabs"][0]["id"]

# 3. Navigate to Gemini
mcp__claude-in-chrome__navigate(
    tabId=tab_id,
    url="https://gemini.google.com/app"
)
time.sleep(3)

# 4. Enter prompt
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=tab_id,
    text="""
        const editor = document.querySelector('[role="textbox"]');
        if (editor) {
            editor.textContent = "Create an image: a photorealistic sunset over mountains";
            editor.dispatchEvent(new Event('input', { bubbles: true }));
            "Prompt entered";
        } else {
            "Editor not found";
        }
    """
)

# 5. Click send
mcp__claude-in-chrome__javascript_tool(
    action="javascript_exec",
    tabId=tab_id,
    text="""
        const btn = document.querySelector('button[aria-label*="Send"]');
        if (btn) { btn.click(); "Sent"; } else { "Button not found"; }
    """
)

# 6. Poll for completion
for i in range(6):  # 30 seconds max
    result = mcp__claude-in-chrome__javascript_tool(
        action="javascript_exec",
        tabId=tab_id,
        text="""
            document.querySelectorAll('img[src*="googleusercontent"]').length > 0
            ? "Ready" : "Generating..."
        """
    )
    if "Ready" in result:
        break
    time.sleep(5)

# 7. Take screenshot
mcp__claude-in-chrome__computer(
    action="screenshot",
    tabId=tab_id
)
```

## Troubleshooting Guide

### "Editor not found" error
**Cause:** Page not fully loaded or selector changed
**Fix:** Wait longer (5 seconds) and retry. Check if Gemini UI has changed.

### "Send button not found" error
**Cause:** Button selector changed or button is disabled
**Fix:** Use fallback selectors. Check if input is empty (button may be disabled).

### TypeError on textContent
**Cause:** Used `.value` on contenteditable div
**Fix:** Use `textContent` property instead of `value`.

### No images after 30 seconds
**Cause:** Generation timeout or slow processing
**Fix:** Notify user to check tab manually. Gemini may show error message.

### Tool parameter errors
**Cause:** Used wrong parameter name
**Fix:** Use `text=` for javascript_tool, not `code=` or `script=`.

### Tab not responding
**Cause:** Tab closed or crashed
**Fix:** Call tabs_context_mcp again to get fresh context.
