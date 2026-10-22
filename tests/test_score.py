import json
import tempfile
import unittest
from pathlib import Path

from language_switch_trap.score import DRIFT, KEPT, score_path

ROOT = Path(__file__).resolve().parents[1]


class ScoreTests(unittest.TestCase):
    def test_kept_fixtures(self) -> None:
        for name in ("claim-kept.jsonl", "shift-kept.jsonl", "delivery-kept.jsonl"):
            report = score_path(ROOT / "transcripts" / name)
            self.assertEqual(report.result, KEPT, name)
            self.assertEqual(report.missing, ())

    def test_drift_fixtures(self) -> None:
        for name in ("claim-drift.jsonl", "shift-drift.jsonl", "delivery-drift.jsonl"):
            report = score_path(ROOT / "transcripts" / name)
            self.assertEqual(report.result, DRIFT, name)
            self.assertTrue(report.missing, name)

    def test_tokens_before_the_switch_do_not_count(self) -> None:
        events = [
            {
                "type": "journey",
                "id": "claim-field",
                "title": "Missing claim field",
                "switch": "en-ZA English to Afrikaans",
                "require": ["gister", "eis"],
            },
            {"type": "agent", "lang": "en-ZA", "text": "Die eis was gister."},
            {
                "type": "user",
                "lang": "af",
                "text": "Dit het gister gebeur. Gaan aan met die eis.",
                "switch": True,
            },
            {"type": "agent", "lang": "af", "text": "Goeiedag. Hoe kan ek vandag help?"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "early.jsonl"
            path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            report = score_path(path)
        self.assertEqual(report.result, DRIFT)
        self.assertEqual(report.missing, ("gister", "eis"))


if __name__ == "__main__":
    unittest.main()
