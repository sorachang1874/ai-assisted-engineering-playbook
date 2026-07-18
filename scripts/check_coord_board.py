#!/usr/bin/env python3
"""Validate a `.coord/BOARD.md` live coordination snapshot.

The board is the single source of truth for live lane progress: every active
lane carries one resume card that a cold, different-tool resumer can execute
from. This validator fails closed on missing sections, missing card fields,
unknown states, duplicate exclusive write paths across lanes, and referenced
coordination files that do not exist.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = (
    "## Authority and resume rules",
    "## Recorded directives",
    "## Integration spine",
    "## Active lane resume cards",
    "## Gates and known environment state",
    "## Next integration sweep",
)

LANE_HEADER_RE = re.compile(r"^###\s+lane\s+`(?P<lane>[^`]+`)\s+—\s*(?P<title>.*)$")
FIELD_RE = re.compile(r"^-\s+(?P<name>[A-Za-z][A-Za-z /]*):\s*(?P<value>.*)$")
STATE_RE = re.compile(
    r"^(dispatched|in_progress|validating|delivered|integrated|blocked|pending)"
    r"(-[a-z_]+)*$"
)

REQUIRED_CARD_FIELDS = ("Goal", "Base", "Exclusive writes", "State", "Last validation", "Next")

COORD_REF_RE = re.compile(r"`(\.coord/[^`]+)`")


def _split_lane_cards(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Return (pre-card section lines, [(lane_id, card_lines)])."""
    lines = text.splitlines()
    header_lines: list[str] = []
    cards: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    in_cards = False
    for line in lines:
        if line.startswith("## Active lane resume cards"):
            in_cards = True
            header_lines.append(line)
            continue
        if in_cards and line.startswith("## ") and not line.startswith("### "):
            if current_name is not None:
                cards.append((current_name, current_lines))
                current_name, current_lines = None, []
            in_cards = False
            header_lines.append(line)
            continue
        if not in_cards:
            header_lines.append(line)
            continue
        match = LANE_HEADER_RE.match(line)
        if match:
            if current_name is not None:
                cards.append((current_name, current_lines))
            current_name = match.group("lane")
            current_lines = [line]
        elif current_name is not None:
            current_lines.append(line)
        else:
            header_lines.append(line)
    if current_name is not None:
        cards.append((current_name, current_lines))
    return header_lines, cards


def validate_board(board_path: Path, repo: Path) -> list[str]:
    errors: list[str] = []
    text = board_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing required section: {section}")

    _, cards = _split_lane_cards(text)
    if not cards:
        errors.append("no lane resume cards found")

    claimed_writes: dict[str, str] = {}
    for lane_id, card_lines in cards:
        fields: dict[str, str] = {}
        last_field: str | None = None
        for line in card_lines:
            match = FIELD_RE.match(line.strip())
            if match:
                last_field = match.group("name").strip().lower()
                fields[last_field] = match.group("value").strip()
            elif line.startswith((" ", "\t")) and last_field is not None:
                fields[last_field] += " " + line.strip()
        for label in REQUIRED_CARD_FIELDS:
            if not any(name.startswith(label.lower()) for name in fields):
                errors.append(f"lane `{lane_id}`: missing field `{label}`")
        state = next((v for k, v in fields.items() if k.startswith("state")), "")
        token = re.search(r"`([A-Za-z_][A-Za-z_-]*)`", state)
        state_value = token.group(1) if token else state.split(" ")[0].strip("`")
        if state_value and not STATE_RE.match(state_value):
            errors.append(f"lane `{lane_id}`: unknown state `{state_value}`")
        own_writes = set(re.findall(r"`([^`]+)`", fields.get("exclusive writes", "")))
        for ref in own_writes:
            if ref in claimed_writes:
                errors.append(
                    f"write path `{ref}` claimed by both `{claimed_writes[ref]}` and `{lane_id}`"
                )
            else:
                claimed_writes[ref] = lane_id
        for ref in COORD_REF_RE.findall("\n".join(card_lines)):
            if ref in own_writes:
                continue
            ref_path = Path(ref)
            if not ref_path.is_absolute():
                ref_path = repo / ref
            if not ref_path.is_file():
                errors.append(f"lane `{lane_id}`: referenced `{ref}` does not exist")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", help="path to BOARD.md")
    parser.add_argument(
        "--repo",
        default=None,
        help="repository root used to resolve relative .coord references "
        "(default: two directories above the board file)",
    )
    args = parser.parse_args()
    board_path = Path(args.board)
    repo = Path(args.repo) if args.repo else board_path.resolve().parents[2]
    errors = validate_board(board_path, repo)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 1
    print(f"VALID: {board_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
