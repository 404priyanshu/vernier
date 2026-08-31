from __future__ import annotations

import re
from dataclasses import dataclass, field

HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
GIT_DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")
PLUS_FILE = re.compile(r"^\+\+\+ (?:b/)?(.+)$")
MINUS_FILE = re.compile(r"^--- (?:a/)?(.+)$")


@dataclass(frozen=True)
class DiffLine:
    kind: str  # "add" | "del" | "ctx"
    new_line: int | None
    old_line: int | None
    text: str


@dataclass
class Hunk:
    file_path: str
    old_start: int
    new_start: int
    header: str
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def added_text(self) -> str:
        return "\n".join(line.text for line in self.lines if line.kind == "add")

    @property
    def unified(self) -> str:
        rows = [self.header]
        for line in self.lines:
            prefix = {"add": "+", "del": "-", "ctx": " "}[line.kind]
            rows.append(f"{prefix}{line.text}")
        return "\n".join(rows)

    @property
    def new_line_span(self) -> tuple[int | None, int | None]:
        added = [line.new_line for line in self.lines if line.kind == "add" and line.new_line]
        if not added:
            return self.new_start, self.new_start
        return min(added), max(added)

    def normalize(self) -> str:
        body = "\n".join(f"{line.kind}:{line.text.rstrip()}" for line in self.lines)
        return f"{self.file_path}\n{body}"


@dataclass
class FileDiff:
    path: str
    hunks: list[Hunk] = field(default_factory=list)


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    """Parse a unified or git diff into per-file hunks."""
    if not diff_text or not diff_text.strip():
        return []

    files: list[FileDiff] = []
    current_file: FileDiff | None = None
    current_hunk: Hunk | None = None
    new_line = 0
    old_line = 0
    pending_git_path: str | None = None

    for raw in diff_text.splitlines():
        git_match = GIT_DIFF_HEADER.match(raw)
        if git_match:
            if current_hunk and current_file:
                current_file.hunks.append(current_hunk)
            if current_file:
                files.append(current_file)
            pending_git_path = git_match.group(2)
            current_file = FileDiff(path=pending_git_path)
            current_hunk = None
            continue

        plus_match = PLUS_FILE.match(raw)
        if plus_match:
            path = plus_match.group(1)
            if path == "/dev/null":
                continue
            if current_file is None:
                current_file = FileDiff(path=path)
            elif current_file.path in {"", "/dev/null"}:
                current_file.path = path
            continue

        minus_match = MINUS_FILE.match(raw)
        if minus_match:
            continue

        hunk_match = HUNK_HEADER.match(raw)
        if hunk_match:
            if current_file is None:
                current_file = FileDiff(path=pending_git_path or "unknown")
            if current_hunk:
                current_file.hunks.append(current_hunk)
            old_start = int(hunk_match.group(1))
            new_start = int(hunk_match.group(3))
            current_hunk = Hunk(
                file_path=current_file.path,
                old_start=old_start,
                new_start=new_start,
                header=raw,
            )
            old_line = old_start
            new_line = new_start
            continue

        if current_hunk is None:
            continue
        if raw.startswith("\\"):
            continue
        if raw.startswith("+"):
            current_hunk.lines.append(
                DiffLine(kind="add", new_line=new_line, old_line=None, text=raw[1:])
            )
            new_line += 1
        elif raw.startswith("-"):
            current_hunk.lines.append(
                DiffLine(kind="del", new_line=None, old_line=old_line, text=raw[1:])
            )
            old_line += 1
        elif raw.startswith(" "):
            current_hunk.lines.append(
                DiffLine(kind="ctx", new_line=new_line, old_line=old_line, text=raw[1:])
            )
            new_line += 1
            old_line += 1
        else:
            # Some patches omit the leading space on context lines.
            current_hunk.lines.append(
                DiffLine(kind="ctx", new_line=new_line, old_line=old_line, text=raw)
            )
            new_line += 1
            old_line += 1

    if current_hunk and current_file:
        current_file.hunks.append(current_hunk)
    if current_file:
        files.append(current_file)

    return [file_diff for file_diff in files if file_diff.hunks]


def flatten_hunks(files: list[FileDiff]) -> list[Hunk]:
    hunks: list[Hunk] = []
    for file_diff in files:
        hunks.extend(file_diff.hunks)
    return hunks


def github_files_to_diff(files: list[dict]) -> str:
    """Rebuild a unified diff from GitHub pull-request file payloads."""
    chunks: list[str] = []
    for item in files:
        path = item.get("filename") or "unknown"
        patch = item.get("patch")
        if not patch:
            continue
        chunks.append(f"diff --git a/{path} b/{path}")
        chunks.append(f"--- a/{path}")
        chunks.append(f"+++ b/{path}")
        chunks.append(patch)
    return "\n".join(chunks)
