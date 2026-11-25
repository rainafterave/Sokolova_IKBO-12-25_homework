"""Exercise standard input, JSON files, errors and the three examples."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from json_output import write_json

PROJECT = Path(__file__).resolve().parents[2]
ENTRY = PROJECT / "src/main.py"


def run_cli(source, output):
    """Run the real CLI with bytes on stdin from a different directory."""
    return subprocess.run(
        [sys.executable, str(ENTRY), "--output", str(output)],
        input=source, capture_output=True, cwd=output.parent,
    )


class CommandTests(unittest.TestCase):
    """Verify the user-facing conversion path without network requests."""

    def test_all_three_examples(self):
        expected = {
            "server": ("CONNECTIONS", 16.0),
            "education": ("HOURS", 18.0),
            "robot": ("NAME", "Робот"),
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            for name, (field, value) in expected.items():
                with self.subTest(name=name):
                    source = PROJECT / f"src/examples/{name}.conf"
                    result = run_cli(source.read_bytes(), output)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, b"")
                    self.assertEqual(result.stderr, b"")
                    document = json.loads(output.read_text(encoding="utf-8"))
                    self.assertEqual(document[field], value)

    def test_failed_translation_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_bytes(b'{"OLD": 1}')
            for source in [b"begin bad end", b"^(UNKNOWN)", b"\xff"]:
                with self.subTest(source=source):
                    result = run_cli(source, output)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(b"Error:", result.stderr)
                    self.assertEqual(output.read_bytes(), b'{"OLD": 1}')

    def test_utf8_bom_and_spaces_in_output_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "my result.json"
            result = run_cli(b'\xef\xbb\xbf"Hello"', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), "Hello")

    def test_missing_required_output_option(self):
        result = subprocess.run(
            [sys.executable, str(ENTRY)], input=b"1.", capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"--output", result.stderr)

    def test_directory_cannot_be_replaced_by_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "existing"
            output.mkdir()
            result = run_cli(b"1.", output)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(output.is_dir())
            self.assertEqual(list(root.iterdir()), [output])

    def test_atomic_replace_failure_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "result.json"
            output.write_text("original", encoding="utf-8")
            failure = OSError("blocked")
            with patch("json_output.os.replace", side_effect=failure):
                with self.assertRaises(OSError):
                    write_json(output, {"NEW": 2.0})
            self.assertEqual(output.read_text(), "original")
            self.assertEqual(list(root.iterdir()), [output])

    def test_json_output_creates_missing_parent_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested/result.json"
            write_json(output, {"TEXT": "Русский текст"})
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                {"TEXT": "Русский текст"},
            )
