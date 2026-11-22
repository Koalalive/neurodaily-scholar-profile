import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate import ProfileError, load, validate_document  # noqa: E402


def valid_document():
    return {
        "format": "neurodaily.profile",
        "version": 1,
        "config": {
            "profile": "fixture-scholar",
            "disciplines": [{"name": "Neuroscience", "keywords": ["brain"], "enabled": True}],
            "global_keywords": ["brain"],
            "search": {"query": "brain", "journal_mode": "prefer", "sort": "relevance"},
            "sources": {"pubmed": {"enabled": True, "max_results": 10, "lookback_days": 2}},
            "windows": {"daily_paper_hours": 36},
            "policy_feeds": ["https://example.org/feed.xml"],
            "journals": [{"name": "Neuron"}],
        },
    }


class ValidateConfigTests(unittest.TestCase):
    def test_valid_profile(self):
        errors, warnings = validate_document(valid_document())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_malformed_json_reports_line_and_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"format": "neurodaily.profile",', encoding="utf-8")
            with self.assertRaises(ProfileError) as caught:
                load(str(path))
        self.assertIn("line 1", str(caught.exception))
        self.assertIn("column", str(caught.exception))

    def test_reports_schema_paths(self):
        document = valid_document()
        document["config"]["sources"]["policy"] = {
            "enabled": True,
            "feed_kinds": {"https://example.org/rss": "industry"},
        }
        document["config"]["journals"][0]["url"] = "ftp://bad"
        document["config"]["email"] = "private@example.org"
        errors, _ = validate_document(document)
        text = "\n".join(errors)
        self.assertIn("sources.policy.feed_kinds", text)
        self.assertIn("journals[0].url", text)
        self.assertIn("config.email is private", text)

    def test_plain_config_is_accepted_with_warning(self):
        config = valid_document()["config"]
        errors, warnings = validate_document(config)
        self.assertEqual(errors, [])
        self.assertTrue(any("plain config" in warning for warning in warnings))

    def test_missing_disciplines_is_an_error(self):
        document = valid_document()
        del document["config"]["disciplines"]
        errors, _ = validate_document(document)
        self.assertTrue(any("config.disciplines" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
