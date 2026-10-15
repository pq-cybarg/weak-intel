#!/usr/bin/env python3
import glob
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SchemaTests(unittest.TestCase):
    def test_research_json_loads(self):
        files = glob.glob(os.path.join(ROOT, "research", "*.json"))
        self.assertGreaterEqual(len(files), 8)
        for f in files:
            with self.subTest(f=os.path.basename(f)):
                with open(f, encoding="utf-8") as fh:
                    doc = json.load(fh)
                self.assertIn("entities", doc)
                self.assertIn("edges", doc)
                self.assertIn("metadata", doc)
                # entities may be empty for edge-only densification/cross-link blocks
                self.assertIsInstance(doc["entities"], list)
                self.assertTrue(doc["entities"] or doc["edges"])
                self.assertTrue(doc["edges"])
                for e in doc["entities"]:
                    self.assertIn("name", e)
                    self.assertIn("type", e)
                    self.assertIn("source", e)
                for ed in doc["edges"]:
                    self.assertIn("from", ed)
                    self.assertIn("to", ed)
                    self.assertIn("kind", ed)
                    self.assertIn("source", ed)
                    self.assertIn("grade", ed)

    def test_no_intent_verbs_on_collectives_unquoted(self):
        # light guard: fail if a file asserts "the NSA wants"
        import re
        pat = re.compile(r"\b(the NSA|China|Moscow|the GRU)\s+(wants|believes|intends)\b", re.I)
        hits = []
        for f in glob.glob(os.path.join(ROOT, "research", "*.json")):
            t = open(f, encoding="utf-8").read()
            if pat.search(t):
                hits.append(os.path.basename(f))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
