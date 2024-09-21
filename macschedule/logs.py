from __future__ import annotations

import os
from collections import deque
from typing import Dict, Optional

from macschedule.job_configs import JobConfig
from macschedule.constants import LOGS_DIR


class LaunchdLogReader:
    """Read launchd log files for a given `JobConfig`."""

    FILESUFFIX: Dict[str, str] = {
        "stdout": "out",
        "stderr": "err",
    }

    def __init__(self, config: JobConfig) -> None:
        self.config = config
        self.full_job_name = config.full_job_name()

    def read(self, stream: str, tail: int) -> Optional[str]:
        logfile = os.path.expanduser(
            os.path.join(LOGS_DIR, f"{self.full_job_name}.{self.FILESUFFIX[stream]}")
        )
        if os.path.exists(logfile):
            with open(logfile, "r") as f:
                log = deque(f, tail)
            return "".join(log).strip()
        return None
