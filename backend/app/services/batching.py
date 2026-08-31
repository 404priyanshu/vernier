from __future__ import annotations

from app.services.diff import Hunk


def pack_batches(hunks: list[Hunk], max_chars: int = 8000) -> list[list[Hunk]]:
    """Pack hunks into character-bounded batches.

    Empty hunks (no added lines) are skipped. A single oversized hunk becomes
    its own batch instead of being dropped.
    """
    batches: list[list[Hunk]] = []
    current: list[Hunk] = []
    size = 0

    for hunk in hunks:
        payload = hunk.unified
        if not hunk.added_text.strip():
            continue
        piece = len(payload)
        if current and size + piece > max_chars:
            batches.append(current)
            current = []
            size = 0
        current.append(hunk)
        size += piece

    if current:
        batches.append(current)
    return batches
