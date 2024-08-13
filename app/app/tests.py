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
        res = calc.add(5, 3)

        self.assertEqual(res, 8)

    def test_sub_numbers(self):
        """Test subtraction numbers"""
        res = calc.sub(10, 5)
        self.assertEqual(res, 5)
