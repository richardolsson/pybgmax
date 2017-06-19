import unittest
from datetime import datetime

import pybgmax


class TestParseFunction(unittest.TestCase):
    def test_parse_text(self):
        data = '\n'.join((
            '01BGMAX               0120150805133822000100P                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        f = pybgmax.parse(data)
        self.assertEquals(f.version, 1)
        self.assertEquals(f.timestamp, datetime(2015,8,5,13,38,22, 100))
        self.assertEquals(f.stage, 'P')
        self.assertFalse(f.is_test)
        self.assertEquals(len(f.payments), 0)

    def test_load_filelike(self):
        with open('tests/samples/multipayment.txt', 'r') as fp:
            f = pybgmax.load(fp)

        self.assertEquals(f.version, 1)
        self.assertEquals(len(f.payments), 4)

    def test_load_path(self):
        f = pybgmax.load('tests/samples/multipayment.txt')

        self.assertEquals(f.version, 1)
        self.assertEquals(len(f.payments), 4)

    def test_load_int(self):
        with self.assertRaises(ValueError):
            f = pybgmax.load(1)
