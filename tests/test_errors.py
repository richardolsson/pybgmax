import unittest

from pybgmax import errors


class TestErrors(unittest.TestCase):
    def test_base_err(self):
        err = errors.BgMaxError('my message')
        self.assertEquals(str(err), 'my message')

    def test_format_err(self):
        err = errors.FormatError('my message')
        self.assertEquals(str(err), 'Bad format: my message')
