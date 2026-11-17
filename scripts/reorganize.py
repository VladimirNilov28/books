#!/usr/bin/env python3
"""Move the repository's tagged books into a category-first folder layout.

Run from the repository root. The default is a dry run; pass --apply to move
tracked files/directories with git mv and update README links.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path.cwd()
TAG_RE = re.compile(r"^\[([^\]]+)\]")
LINK_RE = re.compile(r"(\]\()([^)]*)(\))")


def classify(name: str) -> Path | None:
    match = TAG_RE.match(name)
    if not match:
        return None

    tag = match.group(1).upper().strip()
    title = name[match.end():].lower()
    # Route books by their main subject first; add a language/platform folder
    # only when the collection is specifically about that language/platform.
    if tag in {"ALGORITHMS", "ALGO-TRADING"}:
        return Path("algorithms")
    if tag == "NETWORKING":
        return Path("networking")
    if tag == "CLOUD":
        return Path("cloud")
    if tag == "BIG DATA":
        return Path("data/big-data")
    if tag == "INTERVIEW":
        return Path("career/interviews")
    if tag == "ANDROID":
        return Path("mobile/android")
    if tag == "IOS":
        return Path("mobile/ios")
    if tag == "IPAD":
        return Path("mobile/ipad")
    if tag == "NODE":
        return Path("web/nodejs")
    if tag == "JAVASCRIPT":
        if any(word in title for word in ("algorithm", "data structure")):
            return Path("algorithms/javascript")
        if any(word in title for word in ("architecture", "design pattern")):
            return Path("architecture/javascript")
        return Path("web/javascript")
    if tag == "TYPESCRIPT":
        return Path("web/typescript")
    if tag in {"HTML", "CSS", "WEB", "WEBRTC", "XML", "XSLT"}:
        if tag in {"XML", "XSLT"}:
            return Path("web/markup")
        return Path("web")
    if tag == "JAVA":
        if any(word in title for word in ("algorithm", "data structures")):
            return Path("algorithms/java")
        if any(word in title for word in ("network", "socket")):
            return Path("networking/java")
        if any(word in title for word in ("architecture", "design pattern")):
            return Path("architecture/java")
        if any(word in title for word in ("game", "graphics")):
            return Path("games/java")
        if any(word in title for word in ("web", "servlet", "struts", "hibernate", "spring", "restful", "jax-rs", "jsp")):
            return Path("web/java")
        if any(word in title for word in ("security", "secure coding")):
            return Path("security/java")
        return Path("programming-languages/java")
    if tag == "PYTHON":
        return Path("programming-languages/python")
    if tag in {"ALGO", "PROGRAMMING"}:
        if any(word in title for word in ("algorithm", "алгоритм")):
            return Path("algorithms")
        if any(word in title for word in ("architecture", "архитектур")):
            return Path("architecture")
        if any(word in title for word in ("game", "игр")):
            return Path("games")
        return Path("software-engineering")
    if tag in {"ORACLE", "POSTGRE", "SQL"}:
        return Path("databases/oracle" if tag == "ORACLE" else "databases/postgresql" if tag == "POSTGRE" else "databases/sql")
    if tag == "SECURITY":
        return Path("security")
    if tag == "REGEXP":
        return Path("text-processing/regular-expressions")
    if tag == "UML":
        return Path("architecture/uml")
    if tag == "OS":
        return Path("operating-systems")
    if tag == "JIRA":
        return Path("tools/jira")
    if tag == "VELOCITY":
        return Path("tools/velocity")

    return Path("other")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform the moves (otherwise show a dry run)")
    args = parser.parse_args()

    if not (ROOT / ".git").exists():
        print("Run this script from the root of a git checkout.", file=sys.stderr)
        return 2
    if args.apply:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True, text=True, capture_output=True).stdout
        if status.strip():
            print("Refusing to move files while the working tree has changes; commit or stash them first.", file=sys.stderr)
            return 2

    moves: list[tuple[Path, Path]] = []
    for source in sorted(ROOT.iterdir(), key=lambda item: item.name.casefold()):
        if source.name.startswith(".") or source.name in {"README.md", "scripts", "docs"}:
            continue
        category = classify(source.name)
        if category is None:
            continue
        destination = category / source.name
        if (ROOT / destination).exists():
            print(f"Destination already exists; skipping: {destination}", file=sys.stderr)
            continue
        moves.append((source, destination))

    for source, destination in moves:
        print(f"{source.name} -> {destination.as_posix()}")
        if args.apply:
            (ROOT / destination.parent).mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", "--", source.as_posix(), destination.as_posix()], cwd=ROOT, check=True)

    if args.apply and moves:
        readme = ROOT / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            moved_paths = {source.name: destination.as_posix() for source, destination in moves if source.is_file()}

            def update_link(match: re.Match[str]) -> str:
                target = match.group(2)
                decoded = unquote(target)
                replacement = moved_paths.get(decoded) or moved_paths.get(Path(decoded).name)
                if replacement is None:
                    return match.group(0)
                return f"{match.group(1)}{quote(replacement, safe='/')} {match.group(3)}"

            content = LINK_RE.sub(update_link, content)
            if "## Organized library" not in content:
                intro = (
                    "# Programming books [2015]\n\n"
                    "## Organized library\n\n"
                    "Books are grouped by subject. Where a collection is language- or platform-specific, "
                    "it is nested under that subject (for example, `algorithms/java`, `web/javascript`, "
                    "and `mobile/android`). General and multi-language books stay directly in their subject folder.\n\n"
                    "See [STRUCTURE.md](STRUCTURE.md) for the folder guide.\n\n"
                )
                content = intro + content.split("\n", 1)[1] if content.startswith("# ") else intro + content
            readme.write_text(content, encoding="utf-8")
        print(f"Moved {len(moves)} root entries and updated README links.")
    elif not args.apply:
        print(f"\nDry run: {len(moves)} entries would move. Re-run with --apply to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
