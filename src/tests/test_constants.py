"""Cover constant declarations, postfix expressions and invalid operations."""

import unittest

from language import LanguageError, parse
from expressions import apply_operation


class ConstantTests(unittest.TestCase):
    """Exercise numbers, strings and dictionaries as constant values."""

    def test_declared_number_and_integer_expression_operand(self):
        self.assertEqual(parse("set N = 2.5 ^(N 1 +)"), 3.5)

    def test_strings_and_dictionaries_as_constants(self):
        source = (
            'set TEXT = "Привет" '
            "set SETTINGS = begin N := 2.; end "
            "begin TITLE := ^(TEXT); CONFIG := ^(SETTINGS); end"
        )
        self.assertEqual(
            parse(source), {"TITLE": "Привет", "CONFIG": {"N": 2.0}},
        )

    def test_nested_expressions_and_function_spellings(self):
        for function in ["sqrt", "sqrt()"]:
            with self.subTest(function=function):
                self.assertEqual(parse(f"^(^(9. {function}) 2 +)"), 5.0)
        for function in ["pow", "pow()"]:
            with self.subTest(function=function):
                self.assertEqual(parse(f"^(2. 3 {function})"), 8.0)

    def test_postfix_operand_order(self):
        self.assertEqual(parse("^(2. 3 pow 4 + 5 pow)"), 248832.0)

    def test_constants_in_nested_dictionaries(self):
        source = (
            "set BASE = 4. "
            "begin INNER := begin set LOCAL = ^(BASE 1 +) "
            "VALUE := ^(LOCAL); end; OUTER := ^(BASE); end"
        )
        self.assertEqual(
            parse(source), {"INNER": {"VALUE": 5.0}, "OUTER": 4.0},
        )

    def test_dictionary_and_string_operands_can_be_returned(self):
        self.assertEqual(parse('^("hello")'), "hello")
        self.assertEqual(parse("^(begin X := 1.; end)"), {"X": 1.0})

    def test_invalid_constant_declarations(self):
        invalid = [
            "set A = ^(A) 1.", "set A = ^(B) set B = 1. 1.",
            "set A = 1. set A = 2. ^(A)", "^(MISSING)",
            "begin X := begin set L = 1. end; Y := ^(L); end",
        ]
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaises(LanguageError):
                    parse(source)

    def test_bad_postfix_stacks_and_types(self):
        invalid = [
            "^()", "^(+)", "^(1. +)", "^(1. 2.)", '^(1. "a" +)',
            "^(begin end sqrt)", "^(1. 2. + +)", "^(4. /)",
        ]
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaises(LanguageError):
                    parse(source)

    def test_domain_errors_and_overflow(self):
        with self.assertRaisesRegex(LanguageError, "pow"):
            parse("^(10. 10000. pow)")
        with self.assertRaisesRegex(LanguageError, "sqrt"):
            apply_operation([-1.0], "sqrt")

    def test_comments_between_expression_items(self):
        self.assertEqual(parse("set A = 4. ^(A #= gap =# sqrt 1 +)"), 3.0)
