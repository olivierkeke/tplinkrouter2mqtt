import re
from dataclasses import dataclass

from typing import Dict


@dataclass
class WifiData:
    Status: bool
    SSID: str
    bandWidth: str
    QSS: bool
    SecMode: str
    Key: str

    def __post_init__(self):
        self.Status = self.Status == "Up"
        self.QSS = self.QSS == "Enable"


pattern = re.compile(r'(?P<key>\w+)=(?P<value>.+)\r\r')


def frame_to_dict(frame: str) -> Dict[str, str]:
    output = {}
    for m in pattern.finditer(frame):
        output[m.group('key')] = m.group('value')
    return output
