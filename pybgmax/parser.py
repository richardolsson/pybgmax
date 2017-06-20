import re
from datetime import datetime

from pybgmax import errors, content


def parse(data):
    parser = BgMaxParser()
    return parser.parse(data)


class BgMaxParser(object):

    def __init__(self):
        self.__lidx = 0
        self.__lines = []
        self.__header = None
        self.__payments = []
        self.__deductions = []
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
        while self.__lidx < len(self.__lines):
            line = self.__lines[self.__lidx]
            tc = line[0:2]
            if tc == '70':
                self.__parse_footer()
                self.__lidx += 1
                break
            elif tc == '05':
                self.__parse_section()
            else:
                raise errors.FormatError('Unknown TC %s' % tc)

        # Check for trailing data
        while self.__lidx < len(self.__lines):
            line = self.__lines[self.__lidx].strip()
            self.__lidx += 1
            if len(line) > 0:
                raise errors.FormatError('Trailing data is not allowed')

        return content.BgMaxFile(
            format_version=self.__header[1],
            timestamp=self.__header[2],
            stage=self.__header[3],
            deposits=self.__deposits,
            payments=self.__payments,
            deductions=self.__deductions
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
        deductions = []

        self.__lidx += 1
        while self.__lidx < len(self.__lines):
            line = self.__lines[self.__lidx]
            tc = line[0:2]

            if tc == '20':
                payment = self.__parse_payment()
                payments.append(payment)
            elif tc == '21':
                deduction = self.__parse_payment(deduction=True)
                deductions.append(deduction)
            elif tc == '70':
                raise errors.FormatError('Missing deposit line')
            elif tc == '15':
                # End of deposit
                account = line[2:37].lstrip('0')
                date = line[37:45]
                serial = line[45:50].lstrip('0')

                deposit = content.Deposit(
                    bg, pg, cur, date, account, serial, payments, deductions)
                self.__deposits.append(deposit)

                self.__lidx += 1
                return
            else:
                # Skip unknown line within deposit
                self.__lidx += 1

    def __parse_payment(self, deduction=False):
        line = self.__lines[self.__lidx]
        tc = line[0:2]

        references = []
        payment_informations = []

        name = None
        extra_name = None
        payment_information = None

        payment_address = None
        address = None
        post_code = None
        town = None
        country = None
        country_code = None

        org_no = None
        deduction_code = None

        bg = None
        bg_str = line[2:12].lstrip('0')
        if bg_str is not None and len(bg_str) > 0:
            bg = content.BgNo(bg_str)

        reference = self.__parse_reference(line)
        references.append(reference)

        amount = float(line[37:55]) / 100.0
        channel = int(line[56])
        serial = line[57:69].strip()
        has_image = (line[69] == '1')
        if deduction:
            str_deduction_code = line[70]
            if str_deduction_code != ' ':
                deduction_code = int(str_deduction_code)

        self.__lidx += 1
        while self.__lidx < len(self.__lines):
            line = self.__lines[self.__lidx]
            tc = line[0:2]

            if tc == '20' or tc == '21' or tc == '15' or tc == '70':
                # End of payment (new one started or deposit ends here)
                payment_address = content.PaymentAddress(
                    address, post_code, town, country, country_code)
                sender = content.PaymentSender(
                    bg, name, payment_address, org_no)

                if deduction:
                    entity = content.Deduction(
                        amount, sender, references, channel, serial,
                        has_image, payment_informations, deduction_code)
                    self.__deductions.append(entity)
                else:
                    entity = content.Payment(
                        amount, sender, references, channel, serial,
                        has_image, payment_informations)
                    self.__payments.append(entity)

                return entity
            elif tc == '22' or tc == '23':
                reference = self.__parse_reference(line)
                references.append(reference)
            elif tc == '25':
                information_text = line[2:].strip()
                payment_information = content.PaymentInformation(
                    information_text)
                payment_informations.append(payment_information)
            elif tc == '26':
                name = line[2:37].strip()
                extra_name = line[37:72].strip()
            elif tc == '27':
                address = line[2:37].strip()
                post_code = line[37:46].strip()
            elif tc == '28':
                town = line[2:37].strip()
                country = line[37:72].strip()
                country_code = line[72:74].strip()
            elif tc == '29':
                org_no = content.OrgNo(line[2:].strip().lstrip('0'))

            self.__lidx += 1

    def __parse_reference(self, line):
        ref_str = line[12:37].strip()
        ref_type = int(line[55])

        return content.PaymentReference(ref_str, ref_type)

    def __parse_footer(self):
        line = self.__lines[self.__lidx]
        num_payments = int(line[2:10])
        num_deductions = int(line[10:18])
        num_extra_refs = int(line[18:26])
        num_deposits = int(line[26:34])

        # TODO: Check numsums
