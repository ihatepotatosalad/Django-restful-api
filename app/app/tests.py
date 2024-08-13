"""
Sample test
"""

from django.test import SimpleTestCase
from app import calc


class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        """
        Test adding numbers
        """
        res = calc.add(5,3)

        self.assertEqual(res,8)