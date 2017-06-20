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
        self.assertEquals(d.payment_date, '20090603')
        self.assertIsNone(d.pg)
        self.assertEquals(len(d.payments), 1)
        self.assertEquals(d.payments[0], f.payments[0])

        p = f.payments[0]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertIsNone(p.sender.bg)
        self.assertEquals(p.amount, 1.0)
        self.assertIsInstance(p.references[0], content.PaymentReference)
        self.assertEquals(str(p.references[0]), '1500073')
        self.assertEquals(p.references[0].ref_type, pybgmax.REFTYPE_OCR)
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
        self.assertEquals(d.payment_date, '20090603')
        self.assertIsNone(d.pg)
        self.assertEquals(len(d.payments), 2)
        self.assertEquals(d.payments[0], f.payments[0])
        self.assertEquals(d.payments[1], f.payments[1])
        self.assertEquals(d.serial, '36')

        p = f.payments[0]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertIsNone(p.sender.bg)
        self.assertEquals(p.amount, 1.0)
        self.assertIsInstance(p.references[0], content.PaymentReference)
        self.assertEquals(str(p.references[0]), '1500073')
        self.assertEquals(p.references[0].ref_type, pybgmax.REFTYPE_OCR)
        self.assertEquals(p.channel, pybgmax.CHANNEL_EBANK)
        self.assertEquals(p.serial, '497850277070')
        self.assertFalse(p.has_image)

        p = f.payments[1]
        self.assertIsInstance(p.sender, content.PaymentSender)
        self.assertEquals(str(p.sender.bg), '378-3511')
        self.assertEquals(p.amount, 100.0)
        self.assertIsInstance(p.references[0], content.PaymentReference)
        self.assertEquals(str(p.references[0]), '65598')
        self.assertEquals(p.references[0].ref_type, pybgmax.REFTYPE_OCR)
        self.assertEquals(p.channel, pybgmax.CHANNEL_AG)
        self.assertEquals(p.serial, '')
        self.assertFalse(p.has_image)

    def test_deduction(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '210000000000                  1500073000000000000000100214978502770700          ',
            '25Betalning med extra refnr 65test                                              ',
            '26JANE DOE                                                                      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.deductions), 1)

    def test_payment_description(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '25Betalning med extra refnr 65test                                              ',
            '26JANE DOE                                                                      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        p = f.payments[0]

        self.assertEquals(str(p.information_text[0]), 'Betalning med extra refnr 65test')

    def test_payment_sender_address(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '27Storozhenka 14 Storozhenka 14      80000                                      ',
            '28Kyiv                                                                  UA      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 1)

        p = f.payments[0]
        self.assertEquals(p.sender.address.address, 'Storozhenka 14 Storozhenka 14')
        self.assertEquals(p.sender.address.post_code, '80000')
        self.assertEquals(p.sender.address.town, 'Kyiv')
        self.assertEquals(p.sender.address.country, '')
        self.assertEquals(p.sender.address.country_code, 'UA')

    def test_payment_reference(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '200000000000                  1500073000000000000000100214978502770700          ',
            '2200037835117495575                  000000000000100000530000000000301          ',
            '220003783511                   695668000000000000050000230000000000301          ',
            '2200037835118988777                  000000000000040000530000000000301          ',
            '230003783511                   744565000000000000050000230000000000301          ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000001000000000000000000000000                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 1)

        p = f.payments[0]
        self.assertEquals(len(p.references), 5)
        self.assertIsInstance(p.references[0], content.PaymentReference)
        self.assertEquals(str(p.references[0]), '1500073')
        self.assertEquals(p.references[0].ref_type, pybgmax.REFTYPE_OCR)
        self.assertIsInstance(p.references[1], content.PaymentReference)
        self.assertEquals(str(p.references[1]), '7495575')
        self.assertEquals(p.references[1].ref_type, pybgmax.REFTYPE_BAD)
        self.assertIsInstance(p.references[2], content.PaymentReference)
        self.assertEquals(str(p.references[2]), '695668')
        self.assertEquals(p.references[2].ref_type, pybgmax.REFTYPE_OCR)
        self.assertIsInstance(p.references[3], content.PaymentReference)
        self.assertEquals(str(p.references[3]), '8988777')
        self.assertEquals(p.references[3].ref_type, pybgmax.REFTYPE_BAD)
        self.assertIsInstance(p.references[4], content.PaymentReference)
        self.assertEquals(str(p.references[4]), '744565')
        self.assertEquals(p.references[4].ref_type, pybgmax.REFTYPE_OCR)


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
