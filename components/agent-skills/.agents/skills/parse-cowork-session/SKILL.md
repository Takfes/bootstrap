---
name: parse-cowork-session
description: Parse a claude-cowork session JSONL export into a readable markdown transcript. Use this skill whenever the user mentions a "cowork session", a "cowork export", a `.jsonl` file produced by claude-cowork, or asks to convert/render/transcribe/parse a claude-cowork chat log into something readable. Trigger even if the user only references the file by UUID-style filename (e.g. `ffe04da2-9627-424a-8b92-54cc9895b115.jsonl`) or says things like "make my cowork session readable", "extract the chat from this jsonl", "render my cowork transcript", or "I exported a session — can you turn it into markdown?". Always prefer this skill over ad-hoc parsing whenever a claude-cowork export is involved.
---

# Parse Cowork Session

Convert a claude-cowork session JSONL export into a clean, human-readable markdown transcript. Wraps a bundled parser script that filters out tool-use noise and renders only the user/assistant chat turns.

## When to use

Trigger when the user wants a readable version of a claude-cowork session, e.g.:

- "parse this cowork jsonl"
- "convert my cowork export to markdown"
- "render the transcript from this session file"
- "make this `.jsonl` readable"
- "I exported a cowork session, can you clean it up?"

## What the skill produces

A markdown file containing one block per chat turn:

```
### @USER[1/3]

<message text>

---

### @ASSISTANT[2/4]

<message text>

---
```

Where `[j/i]` is `accepted-record-count / source-line-number` (preserves alignment with the raw JSONL for debugging).

## Step-by-step workflow

### Step 1 — Confirm the input file

Ask the user for the path to the `.jsonl` file unless they've already provided one in the conversation.

If the user doesn't have a file yet, **remind them how to produce one** (this is the only way to get the input):

> To produce the JSONL: in your claude-cowork session, run `/export`. This downloads a zip archive — unzip it and locate the `.jsonl` file inside (it will be UUID-named, e.g. `ffe04da2-9627-424a-8b92-54cc9895b115.jsonl`). That file is what this skill parses.

Wait for the user to provide the path before proceeding.

### Step 2 — Ask whether and where to save the output

Use `AskUserQuestion` with three options. Default save location follows the workspace's `output-persistence.md` convention.

**Question:** "Where should I save the parsed transcript?"

**Options:**
- **Default location** — save to `claude.io/searches/claude-cowork-session-{YYYYMMDDHHmm}.md` (timestamp is the current local time)
- **Custom path** — user provides a different path
- **Don't save** — print the transcript inline in the conversation instead

If the user picks "Custom path", ask one follow-up for the path. If they only specify a directory, append the default filename `claude-cowork-session-{YYYYMMDDHHmm}.md`.

### Step 3 — Compute the timestamp

Generate the timestamp once, at the moment of the run, in `YYYYMMDDHHmm` format (local time).

```bash
date +%Y%m%d%H%M
```

Use the same timestamp for both the filename and any header you write into the file. Don't recompute it later — drift between filename and header is confusing.

### Step 4 — Run the parser

The bundled script is at `<skill-dir>/scripts/parse_cowork_session.py`. Resolve `<skill-dir>` from the path of this `SKILL.md`.

**To save to a markdown file:**

```bash
python <skill-dir>/scripts/parse_cowork_session.py <input.jsonl> -o <output.md>
```

The script creates the output directory if it doesn't exist. It prints `Wrote N records to <path>` on success.

**To print inline (no save):**

```bash
python <skill-dir>/scripts/parse_cowork_session.py <input.jsonl>
```

This produces the legacy plain-text format (`@USER[j/i]` headers + dashes). Capture stdout and present it to the user as a code block in the conversation, or render the records as a markdown response yourself if the volume is small.

### Step 5 — Confirm and offer next steps

If saved: report the output path and the record count from the script's stdout. Offer the user the next logical step:

- "Want me to summarise the conversation?"
- "Want me to extract decisions or open threads from this session?"
- "Should I log this session in `intel/log.md`?"

If displayed inline: just present the transcript and ask if they want it saved after all.

## Output file structure

When saving to disk, the file is purely the rendered transcript (no extra header block) — the parser writes one `### @TYPE[j/i]` heading per turn, the message body as a paragraph, and `---` separators. This matches the user's specified format.

If the user later asks for a header block (date, source file, etc.), you can prepend one without re-running the parser.

## Parser behaviour reference

The bundled script skips:
- Records lacking `parentUuid` (session metadata, not chat)
- Records with `type == "attachment"`
- Records containing `toolUseResult` (tool responses)
- Records containing `sourceToolUseID` (tool-linked assistant turns)

It extracts text from `message.content`:
- If `content` is a non-empty list → `content[0].text`
- If `content` is a string → use it directly
- Otherwise → skip the record

Records with empty extracted text are skipped. Only the first content block is inspected because cowork JSONL stores the primary text there; later blocks are tool calls or ancillary data not relevant to a readable transcript.

## Common pitfalls

- **Wrong file type** — claude-cowork's `/export` produces a zip; the user must unzip it first. The skill takes the inner `.jsonl`, not the zip.
- **Truncated transcript** — if records seem missing, the user may have confused a tool-output JSONL with a session JSONL. Verify with `head -1 <file> | python -c "import json,sys; print(json.loads(sys.stdin.read()).keys())"` — a session record should have `parentUuid`, `type`, `message`.
- **Timestamp drift** — compute the timestamp once and reuse it; don't call `date` separately for the filename and again later.
- **Unicode in JSONL** — the parser uses default text mode; should be fine for UTF-8. If a user reports mojibake, suggest re-running with `LC_ALL=en_US.UTF-8`.
