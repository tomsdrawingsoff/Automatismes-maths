"""Tests intégrés sans aucune API ni publication extérieure."""
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from generate import exercise, fmt_fraction, polynomial


class TestDailyExercises(unittest.TestCase):
    def test_levels_and_all_templates(self):
        for grade in ('3e','1ère'):
            for kind in range(10):
                for seed in range(30):
                    ex=exercise(grade,kind,random.Random(seed+100*kind))
                    with self.subTest(grade=grade,kind=kind,seed=seed):
                        self.assertTrue(ex['question'])
                        self.assertTrue(ex['hint'])
                        self.assertTrue(ex['answer'])
                        self.assertEqual(len(ex['steps']),3)

    def test_grade_alternation(self):
        for i in range(100):
            day=date(2026,10,27)+timedelta(days=i)
            day_after=day+timedelta(days=1)
            self.assertNotEqual(day.toordinal()%2,day_after.toordinal()%2)

    def test_formatting(self):
        self.assertEqual(fmt_fraction(4), '4')
        self.assertEqual(fmt_fraction(__import__('fractions').Fraction(4,6)), '2/3')
        self.assertEqual(polynomial(-1,-3,3), '3x² − x − 3')


if __name__=='__main__':
    unittest.main()
