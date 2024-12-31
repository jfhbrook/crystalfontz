from enum import Enum
from typing import Dict, Self, Type


class ReportCode(Enum):
    KEY_ACTIVITY = 0x80
    # 0x81 is reserved
    TEMP_REPORT = 0x82

    @classmethod
    def from_bytes(cls: Type[Self], code: bytes) -> "ReportCode":
        return REPORT_CODES[code[0]]


REPORT_CODES: Dict[int, ReportCode] = {
    0x80: ReportCode.KEY_ACTIVITY,
    0x82: ReportCode.TEMP_REPORT,
}
