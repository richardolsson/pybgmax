from datetime import datetime

import errors
import content


def parse(data):
    parser = BgMaxParser()
    return parser.parse(data)


class BgMaxParser(object):
    def __init__(self):
        self.__lidx = 0
        self.__lines = []
        self.__header = None
        self.__payments = []
        self.__deposits = []

    def parse(self, data):
        if data is None:
            raise TypeError('File data must be string, not None')

        if len(data) == 0:
            raise ValueError('File data must not be empty')

        self.__lines = data.split('\n')
        if len(self.__lines) < 2:
            raise errors.FormatError('Must have header and footer')

        self.__parse_header()

        self.__lidx = 1
        while self.__lidx < len(self.__lines)-1:
            line = self.__lines[self.__lidx]
            tc = line[0:2]
            if tc == '70':
                self.__parse_footer()
                self.__lidx += 1
                if self.__lidx < len(self.__lines):
                    raise errors.FormatError('Trailing data is not allowed')
            elif tc == '05':
                self.__parse_section()
            else:
                raise errors.FormatError('Unknown TC %s' % tc)

        return content.BgMaxFile(
            format_version = self.__header[1],
            timestamp = self.__header[2],
            stage = self.__header[3],
            deposits = self.__deposits,
            payments = self.__payments,
        )

    def __parse_header(self):
        line = self.__lines[0]
        if line[0:2] != '01':
            raise errors.FormatError('Malformed header')

        fmt = line[2:7]
        if fmt != 'BGMAX':
            raise errors.FormatError('Unknown format %s' % line[2:5])

        version = int(line[22:24])
        if version != 1:
            raise errors.FormatError('Unknown format version %d' % version)

        try:
            timestamp = datetime.strptime(line[24:44], '%Y%m%d%H%M%S%f')
        except ValueError as e:
            raise errors.FormatError('Malformed timestamp: %s' % str(e))

        stage = line[44:45]
        if stage not in 'TP':
            # Must be either test (T) or production (P)
            raise errors.FormatError('Unknown stage %s' % stage)

        self.__header = (fmt, version, timestamp, stage)

    def __parse_section(self):
        line = self.__lines[self.__lidx]

        bg_str = line[2:12].strip()
        pg_str = line[12:22].strip()

        bg = None
        if len(bg_str):
            bg = content.BgNo(bg_str.lstrip('0'))

        pg = None
        if len(pg_str):
            pg = content.PgNo(pg_str.lstrip('0'))

        cur = line[22:25]
        payments = []

        self.__lidx += 1
        while self.__lines[self.__lidx][0:2] == '20':
            payment = self.__parse_payment()
            payments.append(payment)

        line = self.__lines[self.__lidx]
        tc = line[0:2]
        if tc != '15':
            raise errors.FormatError('Missing deposit line')

        account = line[2:37].lstrip('0')
        serial = line[45:50]

        deposit = content.Deposit(bg, pg, cur, account, serial, payments)
        self.__deposits.append(deposit)

        self.__lidx += 1

    def __parse_payment(self):
        line = self.__lines[self.__lidx]
        tc = line[0:2]

        if tc != '20':
            raise errors.FormatError('Unexpected TC "%s", expected "20"' % tc)

        name = None
        address = []
        org_no = None

        bg = None
        bg_str = line[2:12].lstrip('0')
        if bg_str is not None and len(bg_str) > 0:
            bg = content.BgNo(bg_str)

        ref_str = line[12:37].strip()
        ref_type = int(line[55])
        ref = content.PaymentReference(ref_str, ref_type)

        amount = float(line[37:55]) / 100.0
        channel = int(line[56])
        serial = line[57:69].strip()
        has_image = (line[69] == '1')

        self.__lidx += 1
        while self.__lidx < len(self.__lines):
            line = self.__lines[self.__lidx]
            tc = line[0:2]

            if tc == '20' or tc == '15':
                # End of payment (new one started or deposit ends here)
                sender = content.PaymentSender(bg)
                payment = content.Payment(amount, sender, ref, channel,
                                            serial, has_image)

                self.__payments.append(payment)

                return payment

            self.__lidx += 1

    def __parse_footer(self):
        line = self.__lines[self.__lidx]
        num_payments = int(line[2:10])
        num_deductions = int(line[10:18])
        num_extra_refs = int(line[18:26])
        num_deposits = int(line[26:34])

        # TODO: Check numsums
