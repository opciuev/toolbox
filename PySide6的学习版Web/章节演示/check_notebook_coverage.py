"""Check that completed chapter notebooks preserve every HTML heading and code block."""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path


HEADING_RE = re.compile(
    r'<(?:div class="section-heading"[^>]*>\s*'
    r'<span class="section-number">([^<]+)</span>\s*<h2>(.*?)</h2>\s*</div>|'
    r'h3 class="subsection-heading"[^>]*><span>([^<]+)</span>\s*(.*?)</h3>)',
    re.DOTALL,
)
CODE_RE = re.compile(r'<(?:div|pre) class="code-block"[^>]*>(.*?)</(?:div|pre)>', re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
FENCED_CODE_RE = re.compile(r"(?ms)^(`{3,})[^\n]*\n(.*?)^\1[ \t]*$")


def normalize_text(raw: str) -> str:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in raw.strip().splitlines()]
    return "\n".join(lines)


def normalize_html_code(raw: str) -> str:
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
    raw = TAG_RE.sub("", raw)
    return normalize_text(html.unescape(raw))


def notebook_content(path: Path) -> tuple[str, list[str]]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    markdown_sources = [
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    ]
    text = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
    blocks = [
        normalize_text(match.group(2))
        for source in markdown_sources
        for match in FENCED_CODE_RE.finditer(source)
    ]
    return text, blocks


def check_chapter(chapter_dir: Path, web_root: Path) -> list[str]:
    chapter_match = re.match(r"(\d{2})-", chapter_dir.name)
    if not chapter_match:
        return [f"{chapter_dir}: chapter directory must start with two digits"]

    chapter_number = chapter_match.group(1)
    html_path = web_root / f"ch{chapter_number}.html"
    notebook_path = chapter_dir / "lesson.ipynb"
    if not html_path.exists():
        return [f"{html_path}: source HTML is missing"]

    html_source = html_path.read_text(encoding="utf-8")
    source_text, notebook_blocks = notebook_content(notebook_path)
    failures: list[str] = []

    headings = []
    for match in HEADING_RE.finditer(html_source):
        label = html.unescape((match.group(1) or match.group(3)).strip())
        title = TAG_RE.sub("", match.group(2) or match.group(4)).strip()
        headings.append((label, html.unescape(title)))
        if not re.search(rf"(?m)^#+\s+{re.escape(label)}\b", source_text):
            failures.append(f"{chapter_dir.name}: missing heading {label} {title}")

    code_blocks = [normalize_html_code(match.group(1)) for match in CODE_RE.finditer(html_source)]
    required_counts = Counter(block for block in code_blocks if block)
    notebook_counts = Counter(block for block in notebook_blocks if block)
    for block, required in required_counts.items():
        found = notebook_counts[block]
        if found < required:
            preview = block.splitlines()[0][:80]
            failures.append(
                f"{chapter_dir.name}: code block occurs {found}/{required} times: {preview}"
            )

    if not failures:
        print(
            f"PASS {chapter_dir.name}: "
            f"headings {len(headings)}/{len(headings)}, "
            f"code blocks {len(code_blocks)}/{len(code_blocks)}"
        )
    return failures


def main() -> int:
    demos_root = Path(__file__).resolve().parent
    web_root = demos_root.parent
    chapter_dirs = sorted(
        path for path in demos_root.iterdir() if path.is_dir() and (path / "lesson.ipynb").exists()
    )
    failures: list[str] = []
    for chapter_dir in chapter_dirs:
        failures.extend(check_chapter(chapter_dir, web_root))

    if failures:
        print("\n".join(f"FAIL {failure}" for failure in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
