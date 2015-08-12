import unittest

import pybgmax
from pybgmax import parser, content, errors


class TestDeposit(unittest.TestCase):
    def test_single_payment(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.deposits), 1)
        self.assertEquals(len(f.payments), 1)

        d = f.deposits[0]
        self.assertIsInstance(d.bg, content.BgNo)
        self.assertEquals(str(d.bg), '991-2346')
        self.assertEquals(d.currency, 'SEK')
        self.assertIsNone(d.pg)
        self.assertEquals(len(d.payments), 1)
        self.assertEquals(d.payments[0], f.payments[0])

        p = f.payments[0]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertIsNone(p.sender.bg)
        self.assertEquals(p.amount, 1.0)
        self.assertIsInstance(p.ref, content.PaymentReference)
        self.assertEquals(str(p.ref), '1500073')
        self.assertEquals(p.ref.ref_type, pybgmax.REFTYPE_OCR)
        self.assertEquals(p.channel, pybgmax.CHANNEL_EBANK)
        self.assertEquals(p.serial, '497850277070')
        self.assertFalse(p.has_image)

    def test_multi_payment(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '20000378351165598                    00000000000001000024                       ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.deposits), 1)
        self.assertEquals(len(f.payments), 2)

        d = f.deposits[0]
        self.assertIsInstance(d.bg, content.BgNo)
        self.assertEquals(str(d.bg), '991-2346')
        self.assertEquals(d.currency, 'SEK')
        self.assertIsNone(d.pg)
        self.assertEquals(len(d.payments), 2)
        self.assertEquals(d.payments[0], f.payments[0])
        self.assertEquals(d.payments[1], f.payments[1])
        self.assertEquals(d.serial, '36')

        p = f.payments[0]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertIsNone(p.sender.bg)
        self.assertEquals(p.amount, 1.0)
        self.assertIsInstance(p.ref, content.PaymentReference)
        self.assertEquals(str(p.ref), '1500073')
        self.assertEquals(p.ref.ref_type, pybgmax.REFTYPE_OCR)
        self.assertEquals(p.channel, pybgmax.CHANNEL_EBANK)
        self.assertEquals(p.serial, '497850277070')
        self.assertFalse(p.has_image)

        p = f.payments[1]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertEquals(str(p.sender.bg), '378-3511')
        self.assertEquals(p.amount, 100.0)
        self.assertIsInstance(p.ref, content.PaymentReference)
        self.assertEquals(str(p.ref), '65598')
        self.assertEquals(p.ref.ref_type, pybgmax.REFTYPE_OCR)
        self.assertEquals(p.channel, pybgmax.CHANNEL_AG)
        self.assertEquals(p.serial, '')
        self.assertFalse(p.has_image)

    def test_deduction(self):
        # Deductions are not implemented but should not fail
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '210000000000                  1500073000000000000000100214978502770700          ',
            '26JANE DOE                                                                      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 0)


class TestDepositErrors(unittest.TestCase):
    def test_unknown_deposit_tc(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '99THISISANUNKNOWNCODE                                                           ',
            '7000000001000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            parser.parse(data)

    def test_missing_deposit(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '7000000001000000000000000000000000                                              '
        ))

        with self.assertRaises(errors.FormatError):
            parser.parse(data)

    def test_unknown_payment_tc(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '300000000000                  1500073000000000000000100214978502770700          ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 0)
