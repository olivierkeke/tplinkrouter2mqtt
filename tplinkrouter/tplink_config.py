import re
from typing import Dict

REFRESH_CMD = "wlctl show"
WIFI_ON_CMD = "wlctl set --switch on"
WIFI_OFF_CMD = "wlctl set --switch off"
QSS_ON_CMD = "wlctl set --qss on"
QSS_OFF_CMD = "wlctl set --qss off"

pattern = re.compile(r'(?P<key>\w+)=(?P<value>.+)\r\r')


def frame_to_dict(frame: str) -> Dict[str, str]:
    output = {}
    for m in pattern.finditer(frame):
        output[m.group('key')] = m.group('value')
    return output
