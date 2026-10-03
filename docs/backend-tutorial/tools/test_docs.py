"""Tests for documentation tooling only; no application imports or services."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build
import inventory


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(inventory.OUTPUT.read_text(encoding="utf-8"))

    def test_inventory_matches_current_source(self):
        self.assertEqual(self.data, inventory.collect())

    def test_every_definition_has_one_explanation_and_anchor(self):
        outputs, rows = build.generate(self.data)
        ids = [fn["id"] for file in self.data["files"] for fn in file["functions"]]
        self.assertEqual(ids, [row["id"] for row in rows])
        self.assertEqual(len(ids), len(set(ids)))
        for row in rows:
            self.assertGreaterEqual(len(row["explanation"]), 30)
            self.assertEqual(
                outputs[build.DOCS / row["atlas"]].count(f'id="{row["anchor"]}"'), 1
            )
        self.assertGreater(build.verify_links(outputs), 0)

    def test_missing_business_explanation_is_rejected(self):
        file = next(f for f in self.data["files"] if f["path"] == "app/services/query_service.py")
        fn = next(f for f in file["functions"] if f["name"] == "_key")
        incomplete = dict(build.NOTES[file["path"]])
        incomplete.pop("_key")
        with patch.dict(build.NOTES, {file["path"]: incomplete}):
            with self.assertRaisesRegex(ValueError, "Missing function explanation"):
                build.explanation(file, fn, 0)

    def test_generic_setter_rule_cannot_hide_real_logic(self):
        fake = {
            "anonymous": False, "qualname": "set_unknown",
            "name": "set_unknown",
            "source": "def set_unknown(fn):\n    return do_work(fn)",
        }
        with self.assertRaisesRegex(ValueError, "Missing function explanation"):
            build.explanation({"path": "app/rag/embeddings.py"}, fake, 0)

    def test_stale_manual_explanation_is_rejected(self):
        with patch.dict(build.NOTES, {"no_such_file.py": {"obsolete": "已经删除的函数说明不能留作假覆盖。"}}):
            with self.assertRaisesRegex(ValueError, "Stale manual explanation"):
                build.generate(self.data)

    def test_missing_lambda_explanation_is_rejected(self):
        shortened = build.LAMBDA_NOTES["app/ai_service/chat_graph.py"][:1]
        with patch.dict(build.LAMBDA_NOTES, {"app/ai_service/chat_graph.py": shortened}):
            with self.assertRaisesRegex(ValueError, "Lambda explanation count mismatch"):
                build.generate(self.data)

    def test_broken_local_link_is_rejected(self):
        path = build.DOCS / "probe-only-not-written.md"
        missing = build.DOCS / "definitely-not-existing-document.md"
        with self.assertRaisesRegex(ValueError, "Broken link"):
            build.verify_links({path: f"[missing]({missing.as_posix()})"})

    def test_inventory_parses_nested_definitions_without_execution(self):
        source = (
            "raise RuntimeError('AST parsing must not execute this')\n"
            "def outer(value):\n"
            "    def inner():\n"
            "        return value\n"
            "    return lambda: inner()\n"
            "class Example:\n"
            "    async def method(self):\n"
            "        return 1\n"
        )
        with tempfile.TemporaryDirectory(prefix="backend-docs-test-") as directory:
            root = Path(directory)
            path = root / "sample.py"
            path.write_text(source, encoding="utf-8")
            with patch.object(inventory, "ROOT", root):
                result = inventory.python_file(path)
        names = [fn["qualname"] for fn in result["functions"]]
        self.assertEqual(names[:2], ["outer", "outer.inner"])
        self.assertTrue(names[2].startswith("outer.<lambda@"))
        self.assertEqual(names[3], "Example.method")

    def test_facts_do_not_attribute_nested_return_to_parent(self):
        fn = {
            "anonymous": False,
            "source": "def outer():\n    def inner():\n        return 'inner'\n    return 'outer'",
        }
        _, results = build.facts(fn)
        self.assertEqual(results, [("return", "'outer'")])


if __name__ == "__main__":
    unittest.main()
