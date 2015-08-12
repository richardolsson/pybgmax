import unittest

from pybgmax import PgNo, BgNo


class TestBgNo(unittest.TestCase):
    def test_formatting(self):
        bg = BgNo('1234567')
        self.assertEquals(str(bg), '123-4567')

    def test_raw(self):
        bg = BgNo('1234567')
        self.assertEquals(bg.raw, '1234567')

    def test_raw_no(self):
        bg = BgNo('1234567')
        self.assertEquals(bg.raw_no, 1234567)


class TestPgNo(unittest.TestCase):
    def test_formatting(self):
        pg = PgNo('1234567')
        self.assertEquals(str(pg), '123456-7')

    def test_raw(self):
        pg = PgNo('1234567')
        self.assertEquals(pg.raw, '1234567')

    def test_raw_no(self):
        pg = PgNo('1234567')
        self.assertEquals(pg.raw_no, 1234567)
