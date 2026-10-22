"""A task fact counts only in the agent reply after the language switch."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

KEPT = "Task Kept"
DRIFT = "Language Drift"


@dataclass(frozen=True)
class Report:
    path: str
    title: str
    switch: str
    result: str
    reply: str
    missing: tuple[str, ...]


def score_path(path: Path) -> Report:
    events = _load(path)
    journey = next((event for event in events if event.get("type") == "journey"), None)
    if journey is None:
        raise ValueError(f"{path}: missing journey event")
    require = journey.get("require")
    if not isinstance(require, list) or not all(isinstance(token, str) and token for token in require):
        raise ValueError(f"{path}: journey require must be a list of strings")
    switch_at = next(
        (index for index, event in enumerate(events) if event.get("type") == "user" and event.get("switch")),
        None,
    )
    if switch_at is None:
        raise ValueError(f"{path}: missing a user turn with switch true")
    reply = next(
        (event for event in events[switch_at + 1 :] if event.get("type") == "agent"),
        None,
    )
    if reply is None or not isinstance(reply.get("text"), str):
        raise ValueError(f"{path}: missing an agent reply after the switch")
    text = reply["text"].casefold()
    missing = tuple(token for token in require if token.casefold() not in text)
    return Report(
        path=str(path),
        title=str(journey.get("title") or journey.get("id") or path.stem),
        switch=str(journey.get("switch") or ""),
        result=DRIFT if missing else KEPT,
        reply=reply["text"],
        missing=missing,
    )


def format_table(reports: list[Report]) -> str:
    rows = [(report.path, report.switch, report.result) for report in reports]
    kept = sum(report.result == KEPT for report in reports)
    drift = sum(report.result == DRIFT for report in reports)
    rows.append(("TOTAL", f"{len(reports)} journeys", f"{KEPT} {kept}, {DRIFT} {drift}"))
    header = ("transcript", "switch", "result")
    widths = [
        max(len(header[index]), *(len(row[index]) for row in rows))
        for index in range(3)
    ]

    def line(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    body = [line(header), line(tuple("-" * width for width in widths))]
    body.extend(line(row) for row in rows)
    return "\n".join(body)


def format_details(reports: list[Report]) -> str:
    blocks: list[str] = []
    for report in reports:
        missing = ", ".join(report.missing) if report.missing else "none"
        blocks.append(
            "\n".join(
                [
                    report.path,
                    f"  {report.title}",
                    f"  {report.result}",
                    f"  missing: {missing}",
                    f"  reply: {report.reply}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _load(path: Path) -> list[dict]:
    events = []
    text = path.read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
        if not isinstance(event, dict) or "type" not in event:
            raise ValueError(f"{path}:{line_number}: each event needs a type")
        events.append(event)
    return events
