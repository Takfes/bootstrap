"""Parse a claude-cowork session JSONL file into a readable transcript.

Bundled with the ``parse-cowork-session`` skill. Reads a JSONL session export
(produced by ``/export`` in claude-cowork) and writes a clean markdown
transcript or prints to stdout.

Skip rules and text-extraction logic match the original
``projects/parse-claude-cowork-jsonl-chat/main.py``.
"""

import argparse
import json
from pathlib import Path
from typing import Iterator

# Module-level constant: built once instead of per-iteration.
_SEPARATOR = "\n" + "-" * 50 + "\n"


def parse_records(path: Path) -> Iterator[tuple[str, str, int, int]]:
    """Parse a claude-cowork session JSONL file and yield chat records.

    Skips records that:
    - lack ``parentUuid`` (session-level metadata, not chat turns)
    - have ``type == "attachment"``
    - contain ``toolUseResult`` (tool response payloads)
    - contain ``sourceToolUseID`` (tool-linked assistant turns)

    Only the first content block is inspected because cowork JSONL stores the
    primary text in ``content[0]``; subsequent blocks are tool calls or
    ancillary data that don't belong in a readable transcript.

    Args:
        path: Path to the ``.jsonl`` session file.

    Yields:
        A 4-tuple ``(type_upper, text, j, i)`` where:
        - ``type_upper``: ``data["type"]`` uppercased (e.g. ``"USER"``, ``"ASSISTANT"``).
        - ``text``: Extracted message text.
        - ``j``: 1-indexed count of accepted records so far.
        - ``i``: 1-indexed line number in the file.
    """
    j = 0
    with path.open("r") as fh:
        for i, line in enumerate(fh):
            data = json.loads(line)

            if (
                "parentUuid" not in data
                or data.get("type") == "attachment"
                or "toolUseResult" in data
                or "sourceToolUseID" in data
            ):
                continue

            record_type = data["type"]

            message = data.get("message")
            content = message.get("content") if message else None

            if isinstance(content, list) and content:
                parsed = content[0].get("text")
            elif isinstance(content, str):
                parsed = content
            else:
                parsed = None

            if not parsed:
                continue

            j += 1
            yield record_type.upper(), parsed, j, i + 1


def render_stdout(records: Iterator[tuple[str, str, int, int]]) -> int:
    """Write parsed records to stdout in the legacy plain-text format.

    Args:
        records: Iterator of ``(type_upper, text, j, i)`` tuples.

    Returns:
        Number of records written.
    """
    count = 0
    for type_upper, text, j, i in records:
        print(f"@{type_upper}[{j}/{i}]\n{text}{_SEPARATOR}")
        count = j
    return count


def render_markdown(
    records: Iterator[tuple[str, str, int, int]], output_path: Path
) -> int:
    """Write parsed records to a markdown file.

    Each record is rendered as a level-3 heading followed by the message text
    as a plain paragraph, separated by horizontal rules.

    Args:
        records: Iterator of ``(type_upper, text, j, i)`` tuples.
        output_path: Destination ``.md`` file path.

    Returns:
        Number of records written.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w") as fh:
        for type_upper, text, j, i in records:
            fh.write(f"### @{type_upper}[{j}/{i}]\n\n{text}\n\n---\n\n")
            count = j
    return count


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate renderer."""
    parser = argparse.ArgumentParser(
        description=(
            "Parse a claude-cowork session JSONL export into a readable transcript."
        )
    )
    parser.add_argument(
        "input_file",
        help="Path to the .jsonl session file (from /export → unzip).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT.md",
        help="Write output to a markdown file instead of stdout.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        parser.error(f"Input file not found: {input_path}")

    records = parse_records(input_path)

    if args.output:
        count = render_markdown(records, Path(args.output))
        print(f"Wrote {count} records to {args.output}")
    else:
        render_stdout(records)


if __name__ == "__main__":
    main()
