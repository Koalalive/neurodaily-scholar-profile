import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_profile import build  # noqa: E402
from validate_profile import validate  # noqa: E402


def evidence():
    return json.loads((ROOT / "examples" / "scholar-evidence.example.json").read_text())


def nolan_evidence():
    return json.loads((ROOT / "examples" / "nolan-williams" / "evidence.json").read_text())


class BuildProfileTests(unittest.TestCase):
    def test_builds_valid_wrapper(self):
        profile = build(evidence(), "Example Scholar")
        self.assertEqual(profile["format"], "neurodaily.profile")
        self.assertEqual(profile["version"], 1)
        config = profile["config"]
        self.assertEqual(config["profile"], "example-scholar")
        self.assertGreaterEqual(len(config["disciplines"]), 1)
        self.assertTrue(config["global_keywords"])
        self.assertIn("Neuron", [journal["name"] for journal in config["journals"]])
        errors, _ = validate(profile)
        self.assertEqual(errors, [])

    def test_refuses_empty_evidence(self):
        with self.assertRaises(ValueError):
            build({"works": []})

    def test_detects_psychiatry_and_field_journals(self):
        profile = build(nolan_evidence(), "Nolan Williams", "nolan-williams-test")
        config = profile["config"]
        self.assertFalse(config["sources"]["arxiv"]["enabled"])
        self.assertTrue(config["sources"]["biorxiv"]["enabled"])
        self.assertTrue(config["sources"]["trials"]["enabled"])
        self.assertIn("depression", config["search"]["query"].casefold())
        names = [journal["name"] for journal in config["journals"]]
        self.assertIn("JAMA Psychiatry", names)
        self.assertIn("Brain Stimulation", names)
        self.assertNotIn("OSF Preprints (OSF Preprints)", names)
        self.assertFalse(any("osf" in name.casefold() for name in names))
        self.assertEqual(len(names), len({name.casefold() for name in names}))
        self.assertFalse(any(name.endswith(" .") for name in names))

    def test_field_journals_can_be_disabled(self):
        profile = build(nolan_evidence(), "Nolan Williams",
                        include_field_journals=False)
        names = [journal["name"] for journal in profile["config"]["journals"]]
        self.assertNotIn("JAMA Psychiatry", names)
        errors, _ = validate(profile)
        self.assertEqual(errors, [])

    def test_author_mode_uses_author_query(self):
        profile = build(evidence(), "Example Scholar", mode="author")
        self.assertTrue(profile["config"]["search"]["query"].startswith('AU="'))

    def test_no_private_delivery_fields(self):
        profile = build(evidence())
        errors, _ = validate(profile)
        self.assertFalse(any("private" in error for error in errors))
        self.assertNotIn("email", profile["config"])
        self.assertNotIn("api_key", profile["config"])


if __name__ == "__main__":
    unittest.main()
