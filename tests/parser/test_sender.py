import unittest

from pybgmax import parser


class TestSenderInfo(unittest.TestCase):
    def test_sender_bg(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '20000378351165598                    00000000000001000024                       ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000004000000000000000000000001                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(str(f.payments[0].sender.bg), '378-3511')

    def test_sender_org_no(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '20000378351165598                    00000000000001000024                       ',
            '29005500001234                                                                  ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000004000000000000000000000001                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 1)

        p = f.payments[0]
        self.assertEquals(str(p.sender.org_no), '550000-1234')

    def test_sender_address(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '20000378351165598                    00000000000001000024                       ',
            '26Kalles Plat AB                                                                ',
            '27Storgatan 2                        12345                                      ',
            '28Storaker                                                                      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000004000000000000000000000001                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 1)

        p = f.payments[0]
        self.assertEquals(p.sender.name, 'Kalles Plat AB')
        self.assertEquals(p.sender.address[0], 'Storgatan 2 12345')
        self.assertEquals(p.sender.address[1], 'Storaker')

    def test_unknown_sender_field(self):
        data = '\n'.join((
            '01BGMAX               0120120914173035010331P                                   ',
            '050009912346          SEK                                                       ',
            '20000378351165598                    00000000000001000024                       ',
            '26Kalles Plat AB                                                                ',
            '27Storgatan 2                        12345                                      ',
            '99Unknown field                                                                 ',
            '28Storaker                                                                      ',
            '15000000000000000000058410000010098232009060300036000000000000070000SEK00000004 ',
            '7000000004000000000000000000000001                                              '
        ))

        f = parser.parse(data)
        self.assertEquals(len(f.payments), 1)

        p = f.payments[0]
        self.assertEquals(p.sender.name, 'Kalles Plat AB')
        self.assertEquals(p.sender.address[0], 'Storgatan 2 12345')
        self.assertEquals(p.sender.address[1], 'Storaker')
