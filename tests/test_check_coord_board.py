from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_coord_board import validate_board


def _board_text(
    *,
    lane_state: str = "`in_progress`",
    second_lane: bool = False,
    missing_section: str | None = None,
    extra_write: str | None = None,
) -> str:
    sections = [
        "# Board\n",
        "## Authority and resume rules\n\nrules\n",
        "## Recorded directives\n\n- directive\n",
        "## Integration spine\n\n| Commit | Content | Status |\n| --- | --- | --- |\n| `abc` | x | y |\n",
        "## Active lane resume cards\n",
        f"""### lane `lane-one` — first

- Goal: do the first thing.
- Base/branch/worktree: `abc123` / `lane-one` / `/tmp/lane-one`.
- Exclusive writes: `.coord/handoffs/lane-one-v1.md`.
- State: {lane_state} since 2026-07-18.
- Last validation: `pytest -q` -> `1 passed`.
- Next: integrate.
""",
    ]
    if second_lane:
        sections.append(
            f"""### lane `lane-two` — second

- Goal: do the second thing.
- Base/branch/worktree: `abc123` / `lane-two` / `/tmp/lane-two`.
- Exclusive writes: `{extra_write or '.coord/handoffs/lane-two-v1.md'}`.
- State: `blocked` on lane-one.
- Last validation: none (not started).
- Next: wait.
"""
        )
    sections.append("## Gates and known environment state\n\n- gates\n")
    sections.append("## Next integration sweep\n\n1. sweep\n")
    text = "\n".join(sections)
    if missing_section is not None:
        text = text.replace(missing_section, "## Removed section")
    return text


class CoordBoardTests(unittest.TestCase):
    def _write_board(self, root: Path, text: str) -> Path:
        board = root / "BOARD.md"
        board.write_text(text, encoding="utf-8")
        return board

    def test_valid_board_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = self._write_board(root, _board_text(second_lane=True))
            self.assertEqual(validate_board(board, root), [])

    def test_missing_required_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = self._write_board(
                root, _board_text(missing_section="## Recorded directives")
            )
            errors = validate_board(board, root)
            self.assertTrue(any("Recorded directives" in error for error in errors))

    def test_unknown_state_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = self._write_board(root, _board_text(lane_state="`sideways`"))
            errors = validate_board(board, root)
            self.assertTrue(any("unknown state" in error for error in errors))

    def test_duplicate_exclusive_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = self._write_board(
                root,
                _board_text(
                    second_lane=True, extra_write=".coord/handoffs/lane-one-v1.md"
                ),
            )
            errors = validate_board(board, root)
            self.assertTrue(any("claimed by both" in error for error in errors))

    def test_missing_referenced_coord_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _board_text().replace(
                "- Next: integrate.",
                "- Next: integrate after reading `.coord/handoffs/other-lane-v1.md`.",
            )
            board = self._write_board(root, text)
            errors = validate_board(board, root)
            self.assertTrue(any("does not exist" in error for error in errors))

    def test_own_undelivered_handoff_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _board_text().replace(
                "- Exclusive writes: `.coord/handoffs/lane-one-v1.md`.",
                "- Exclusive writes: `.coord/handoffs/lane-one-v1.md`.\n"
                "- Next: review `.coord/handoffs/lane-one-v1.md` on delivery.",
            )
            board = self._write_board(root, text)
            self.assertEqual(validate_board(board, root), [])

    def test_multi_line_bullet_write_path_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = _board_text().replace(
                "- Exclusive writes: `.coord/handoffs/lane-one-v1.md`.",
                "- Exclusive writes: five tracked paths in packet\n"
                "  `.coord/session-packets/lane-one-v1.md` plus handoff\n"
                "  `.coord/handoffs/lane-one-v1.md`.",
            )
            (root / ".coord/session-packets").mkdir(parents=True)
            (root / ".coord/session-packets/lane-one-v1.md").write_text("x")
            board = self._write_board(root, text)
            self.assertEqual(validate_board(board, root), [])


if __name__ == "__main__":
    unittest.main()
