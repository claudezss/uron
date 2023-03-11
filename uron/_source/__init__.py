import dataclasses
import logging
import os
from datetime import datetime
from typing import Dict

FORMAT = "%(level)-8s %(time)-8s %(pid)-8s %(user)-8s %(message)s"
logging.basicConfig(format=FORMAT, level="DEBUG")


@dataclasses.dataclass
class LoggingInfo:
    level: str
    time: str
    pid: int
    user: str


def get_basic_logging_info(level: str) -> Dict[str, str]:
    try:
        user = os.getlogin()
    except Exception:
        user = "UNKNOWN"
    return dataclasses.asdict(
        LoggingInfo(
            level=level,
            time=str(datetime.now()),
            pid=os.getpid(),
            user=user,
        )
    )
