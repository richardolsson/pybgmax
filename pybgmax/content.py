from datetime import datetime

class BgMaxFile(object):
    def __init__(self, format_version, timestamp, stage,
        deposits=[], payments=[]):

        self.__version = format_version
        self.__timestamp = timestamp
        self.__stage = stage
        self.__payments = payments
        self.__deposits = deposits

    @property
    def version(self):
        return self.__version

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def stage(self):
        return self.__stage

    @property
    def is_test(self):
        return self.__stage == 'T'

    @property
    def payments(self):
        return self.__payments

    @property
    def deposits(self):
        return self.__deposits

class Deposit(object):
    def __init__(self, bg, pg, currency, account_no, serial_no, payments):
        self.__bg = bg
        self.__pg = pg
        self.__currency = currency
        self.__account = account_no
        self.__serial = serial_no
        self.__payments = payments

    @property
    def bg(self):
        return self.__bg

    @property
    def pg(self):
        return self.__pg

    @property
    def currency(self):
        return self.__currency

    @property
    def account(self):
        return self.__account

    @property
    def serial(self):
        return self.__serial

    @property
    def payments(self):
        return self.__payments

class PaymentReference(object):
    def __init__(self, ref_str, ref_type):
        self.__ref_str = ref_str
        self.__ref_type = ref_type

    @property
    def ref_type(self):
        return self.__ref_type

    def __str__(self):
        return self.__ref_str

class PaymentSender(object):
    def __init__(self, bg, name, address_lines, org_no):
        self.__bg = bg
        self.__name = name
        self.__address = address_lines
        self.__org_no = org_no

    @property
    def name(self):
        return self.__name

    @property
    def address(self):
        return self.__address

    @property
    def org_no(self):
        return self.__org_no

    @property
    def bg(self):
        return self.__bg

class Payment(object):
    def __init__(self, amount, sender, ref, channel, serial, has_image):
        self.__amount = amount
        self.__sender = sender
        self.__ref = ref
        self.__channel = channel
        self.__serial = serial
        self.__has_image = has_image

    @property
    def amount(self):
        return self.__amount

    @property
    def sender(self):
        return self.__sender

    @property
    def ref(self):
        return self.__ref

    @property
    def channel(self):
        return self.__channel

    @property
    def serial(self):
        return self.__serial

    @property
    def has_image(self):
        return self.__has_image

class FormattedNumber(object):
    def __init__(self, raw):
        self._raw_str = str(raw)
        self._raw_no = int(raw)

    @property
    def raw(self):
        return self._raw_str

    @property
    def raw_no(self):
        return self._raw_no

class BgNo(FormattedNumber):
    def __str__(self):
        s = self._raw_str
        return '%s-%s' % (s[0:3], s[3:])

class PgNo(FormattedNumber):
    def __str__(self):
        s = self._raw_str
        return '%s-%s' % (s[0:-1], s[-1])

class OrgNo(FormattedNumber):
    def __str__(self):
        s = self._raw_str
        return '%s-%s' % (s[0:6], s[6:10])
