"""Check that docs/ stays navigable through its README indexes.

Enforces the AGENTS.md golden rules for docs/:

1. Every folder under docs/ has a README.md.
2. Every other .md file in a folder is linked from that folder's README.md.
3. Every subfolder is linked from its parent folder's README.md.
4. Every relative link in a tracked Markdown file points at a file or folder
   that exists (anchors and external URLs are not checked).

Stdlib only. Run from the repo root:

    uv run --no-project python scripts/check_docs_index.py
"""

import re
import subprocess
import sys
from pathlib import Path

DOCS = Path("docs")
# [text](target) and [text](<target>); images match too, and their paths must
# exist as well.
LINK = re.compile(r"\[[^\]]*\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`[^`]*`")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [Path(line) for line in out.splitlines() if Path(line).is_file()]


def links(md: Path) -> list[str]:
    """Return link targets outside code blocks and inline code spans."""
    targets: list[str] = []
    in_fence = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            targets.extend(LINK.findall(CODE_SPAN.sub("", line)))
    return targets


def is_local(target: str) -> bool:
    return not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) and not target.startswith("#")


def resolve(md: Path, target: str) -> Path:
    return (md.parent / target.split("#", 1)[0]).resolve()


def check_index(errors: list[str]) -> None:
    for folder in sorted(p for p in [DOCS, *DOCS.rglob("*")] if p.is_dir()):
        readme = folder / "README.md"
        if not readme.is_file():
            errors.append(f"{folder}/: missing README.md")
            continue
        linked = {resolve(readme, t) for t in links(readme) if is_local(t)}
        for child in sorted(folder.iterdir()):
            if child == readme:
                continue
            if child.is_dir() and not {child.resolve(), (child / "README.md").resolve()} & linked:
                errors.append(f"{readme}: does not link subfolder {child.name}/")
            elif child.suffix == ".md" and child.resolve() not in linked:
                errors.append(f"{readme}: does not link {child.name}")


def check_links(errors: list[str]) -> None:
    for md in tracked_markdown():
        for target in links(md):
            if is_local(target) and not resolve(md, target).exists():
                errors.append(f"{md}: broken link {target}")


def main() -> int:
    errors: list[str] = []
    check_index(errors)
    check_links(errors)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} problem(s). See AGENTS.md, step 2 (Research).", file=sys.stderr)
        return 1
    print("docs index OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
