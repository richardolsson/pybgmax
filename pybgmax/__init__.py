from content import (
    BgMaxFile,
    Deposit,
    PaymentReference,
    PaymentSender,
    Payment,
    BgNo,
    PgNo,
)

REFTYPE_BLANK = 0
REFTYPE_UNAVAILABLE = 1
REFTYPE_OCR = 2
REFTYPE_MULTI = 3
REFTYPE_REF = 4
REFTYPE_BAD = 5

CHANNEL_EBANK = 1
CHANNEL_LB = 2
CHANNEL_SLIP = 3
CHANNEL_AG = 4
