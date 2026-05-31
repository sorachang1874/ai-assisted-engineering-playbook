#!/usr/bin/env python3
"""Validate local Markdown links.

External links are intentionally not checked here to keep CI deterministic.
Use a separate scheduled workflow if external link health matters.
"""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def main() -> int:
    missing: list[tuple[str, str]] = []
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if is_external(target):
                continue
            local = target.split("#", 1)[0]
            if local and not (path.parent / local).exists():
                missing.append((str(path.relative_to(ROOT)), target))

    if missing:
        for source, target in missing:
            print(f"missing local markdown link: {source} -> {target}")
        return 1

    print("local markdown links ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

