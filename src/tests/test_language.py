"""Cover literals, comments, nesting and invalid grammar."""

import unittest

from language import LanguageError, parse


class LiteralTests(unittest.TestCase):
    """Verify every literal form specified by variant 23."""

    def test_decimal_numbers(self):
        for source, expected in [("0.0", 0.0), ("12.", 12.0), ("1.25", 1.25)]:
            with self.subTest(source=source):
                self.assertEqual(parse(source), expected)

    def test_unicode_and_escaped_strings(self):
        self.assertEqual(parse('"Привет"'), "Привет")
        self.assertEqual(parse(r'"a\n\"b"'), 'a\n"b')

    def test_empty_and_nested_dictionaries(self):
        self.assertEqual(parse("begin end"), {})
        self.assertEqual(
            parse('begin A := begin B := 2.; end; C := "text"; end'),
            {"A": {"B": 2.0}, "C": "text"},
        )

    def test_multiline_comments_and_comment_text_in_strings(self):
        source = '#= first\nsecond =# begin A #= gap =# := "#=x=#"; end'
        self.assertEqual(parse(source), {"A": "#=x=#"})

    def test_syntax_errors(self):
        invalid = [
            "", "1", ".5", "-1.0", "1.0e2", "begin a := 1.; end",
            "begin A1 := 1.; end", "begin A := 1. end",
            "begin A = 1.; end", "begin", "#= unclosed", '"unclosed',
            "1.0 2.0", "begin A := [1.]; end",
        ]
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaisesRegex(LanguageError, "line.*column"):
                    parse(source)

    def test_duplicate_keys_and_overflow(self):
        for source in ["begin A := 1.; A := 2.; end", "9" * 400 + ".0"]:
            with self.subTest(source=source):
                with self.assertRaises(LanguageError):
                    parse(source)
