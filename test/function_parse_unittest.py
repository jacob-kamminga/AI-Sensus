import unittest
import pandas as pd
from parse_function import custom_function_parser as cfp
from parse_function.parse_exception import ParseException


class FunctionParseTestCase(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({'A': [1, 2, 3],
                                'B': [4, 5, 6],
                                'C': [7, 8, 9]})

    def test_correct_syntax(self):
        self.assertEqual("5+5", cfp.parse("5 + 5"),
                         "Plus operation parsed incorrectly")
        self.assertEqual("10-5", cfp.parse("10 - 5"),
                         "Minus operation parsed incorrectly")
        self.assertEqual("4*a", cfp.parse("4 * a"),
                         "Multiplication operation parsed incorrectly")
        self.assertEqual("25/5", cfp.parse("25 / 5"),
                         "Division operation parsed incorrectly")
        self.assertEqual("x**2", cfp.parse("x^2"),
                         "Power operation parsed incorrectly")
        self.assertEqual("(b)**0.5", cfp.parse("sqrt(b)"),
                         "Square root operation parsed incorrectly")
        self.assertEqual("(x+y)*2", cfp.parse("(x + y) * 2"),
                         "Bracket operation parsed incorrectly")
        self.assertEqual("(Ax**2+Ay**2+Az**2)**0.5", cfp.parse("sqrt(Ax^2 + Ay^2 + Az^2)"),
                         "Vector operation parsed incorrectly")

    def test_incorrect_syntax(self):
        self.assertRaises(ParseException, cfp.parse, "(3 + 4")
        self.assertRaises(ParseException, cfp.parse, "a /")
        self.assertRaises(ParseException, cfp.parse, "3 ** x")
        self.assertRaises(ParseException, cfp.parse, "- 4")
        self.assertRaises(ParseException, cfp.parse, "sqrt 5")
        self.assertRaises(ParseException, cfp.parse, "4^")

    def test_pd_eval(self):
        # Calculate mean
        parse_string = cfp.parse("(A + B + C) / 3")
        self.df.eval("D = " + parse_string, inplace=True)

        self.assertEqual((1 + 4 + 7) / 3, self.df['D'][0],
                         "Mean of A, B, and C incorrectly calculated")
        self.assertEqual((2 + 5 + 8) / 3, self.df['D'][1],
                         "Mean of A, B, and C incorrectly calculated")
        self.assertEqual((3 + 6 + 9) / 3, self.df['D'][2],
                         "Mean of A, B, and C incorrectly calculated")

        # Calculate l2-norm
        parse_string = cfp.parse("sqrt(A^2 + B^2 + C^2)")
        self.df.eval("E = " + parse_string, inplace=True)

        self.assertEqual((1**2 + 4**2 + 7**2)**0.5, self.df['E'][0],
                         "l2-norm of A, B, and C incorrectly calculated")
        self.assertEqual((2**2 + 5**2 + 8**2)**0.5, self.df['E'][1],
                         "l2-norm of A, B, and C incorrectly calculated")
        self.assertEqual((3**2 + 6**2 + 9**2)**0.5, self.df['E'][2],
                         "l2-norm of A, B, and C incorrectly calculated")
