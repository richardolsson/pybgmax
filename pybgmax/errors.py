class BgMaxError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class FormatError(BgMaxError):
    def __str__(self):
        return 'Bad format: ' + self.message
