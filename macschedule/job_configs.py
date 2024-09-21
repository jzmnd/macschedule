from __future__ import annotations

import os
import getpass
from dataclasses import dataclass, asdict, field
from typing import Dict, Optional, List

import yaml
from dacite import from_dict

from macschedule.constants import LAUNCHAGENTS_DIR


@dataclass
class Job:
    binpath: str
    file: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class Schedule:
    minute: Optional[int] = None
    hour: Optional[int] = None
    day: Optional[int] = None
    month: Optional[int] = None
    weekday: Optional[int] = None

    def to_dict(self) -> Dict[str, int]:
        return {k.title(): v for k, v in asdict(self).items() if v is not None}


@dataclass
class Interval:
    seconds: int = 0
    minutes: int = 0
    hours: int = 0
    days: int = 0

    def total_seconds(self) -> int:
        return self.seconds + 60 * self.minutes + 3600 * self.hours + 86400 * self.days


@dataclass
class JobConfig:
    name: str
    job: Job
    schedule: Optional[Schedule] = None
    cron: Optional[str] = None
    interval: Optional[Interval] = None
    exittimeout: int = 30
    workingdir: str = "~"

    @classmethod
    def from_file(cls, filepath: str) -> JobConfig:
        with open(filepath, "r") as stream:
            config = yaml.safe_load(stream)
        jobconfig = from_dict(data_class=cls, data=config)
        if jobconfig.schedule or jobconfig.cron or jobconfig.interval:
            return jobconfig
        raise ValueError("Missing one of schedule, cron, or interval in the job configuration.")

    def full_job_name(self) -> str:
        user_name = getpass.getuser()
        return f"local.{user_name}.ms.{self.name}"

    def output_filepath(self) -> str:
        return os.path.expanduser(
            os.path.join(LAUNCHAGENTS_DIR, f"{self.full_job_name()}.agent.plist")
        )
