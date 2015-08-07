from datetime import datetime

class BgMaxFile(object):
    def __init__(self, format_version, timestamp, stage, payments=[]):
        self.__version = format_version
        self.__timestamp = timestamp
        self.__stage = stage
        self.__payments = payments

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
