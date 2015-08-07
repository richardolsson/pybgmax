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

        return content.BgMaxFile(
            format_version = self.__header[1],
            timestamp = self.__header[2],
            stage = self.__header[3]
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

    def __parse_footer(self):
        line = self.__lines[self.__lidx]
        num_payments = int(line[2:10])
        num_deductions = int(line[10:18])
        num_extra_refs = int(line[18:26])
        num_deposits = int(line[26:34])

        # TODO: Check numsums
