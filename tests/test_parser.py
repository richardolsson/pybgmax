import unittest
from datetime import datetime

from pybgmax import parser, errors



class TestStartEnd(unittest.TestCase):
    def test_correctly_formatted_empty(self):
        data = '\n'.join((
            '01BGMAX               0120150805133822000100P                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(f.version, 1)
        self.assertEquals(f.timestamp, datetime(2015,8,5,13,38,22, 100))
        self.assertEquals(f.stage, 'P')
        self.assertFalse(f.is_test)
        self.assertEquals(len(f.payments), 0)

    def test_stage_test(self):
        data = '\n'.join((
            '01BGMAX               0120150805133822000100T                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(f.version, 1)
        self.assertEquals(f.timestamp, datetime(2015,8,5,13,38,22, 100))
        self.assertEquals(f.stage, 'T')
        self.assertTrue(f.is_test)
        self.assertEquals(len(f.payments), 0)

    def test_unknown_format(self):
        data = '\n'.join((
            '01UNKNOWN             0120150805133822900094P                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_unknown_version(self):
        data = '\n'.join((
            '01BGMAX               0220150805133822900094P                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_unknown_stage(self):
        data = '\n'.join((
            '01BGMAX               0120150805133822000100X                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_malformed_timestamp(self):
        data = '\n'.join((
            '01BGMAX               01201508051XX822000100P                                   ',
            '7000000000000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_malformed_header(self):
        data = '\n'.join((
            'This is not a real header                                                       ',
            '7000000000000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_missing_header(self):
        data = (
            '7000000000000000000000000000000000                                              '
        )

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)

    def test_none(self):
        with self.assertRaises(TypeError):
            f = parser.parse(None)

    def test_empty(self):
        with self.assertRaises(ValueError):
            f = parser.parse('')

    def test_trailing(self):
        data = '\n'.join((
            '01BGMAX               0120150805133822000104P                                   ',
            '7000000000000000000000000000000000                                              ',
            'Trailing content should not be here                                             '
        ))

        with self.assertRaises(errors.FormatError):
            f = parser.parse(data)
