from __future__ import annotations

import os

from lxml import etree

from macschedule.launchd_configs import (
    Label,
    ProgramArguments,
    EnvironmentVariables,
    ExitTimeOut,
    WorkingDirectory,
    StandardErrorPath,
    StandardOutPath,
    StartInterval,
    StartCalendarInterval,
)
from macschedule.constants import DOCTYPE, PLIST_VERSION, LOGS_DIR
from macschedule.job_configs import JobConfig
from macschedule.cron import cron_to_schedules


class PListGenerator:
    """Generate .plist files from a given `JobConfig`."""

    def __init__(self, config: JobConfig) -> None:
        self.config = config
        self.full_job_name = config.full_job_name()
        self.plist = etree.Element("plist", version=PLIST_VERSION)
        self.plist_dict = etree.SubElement(self.plist, "dict")

    def populate_plist(self) -> PListGenerator:
        Label(self.plist_dict, f"{self.full_job_name}.agent").generate_elements()
        pargs = [
            os.path.expanduser(self.config.job.binpath),
            os.path.expanduser(self.config.job.file),
            *self.config.job.args,
        ]
        ProgramArguments(self.plist_dict, pargs).generate_elements()
        if self.config.job.env:
            EnvironmentVariables(self.plist_dict, self.config.job.env).generate_elements()
        if self.config.schedule:
            schedules = [self.config.schedule.to_dict()]
            StartCalendarInterval(self.plist_dict, schedules).generate_elements()
        elif self.config.cron:
            schedules = [s.to_dict() for s in cron_to_schedules(self.config.cron)]
            StartCalendarInterval(self.plist_dict, schedules).generate_elements()
        elif self.config.interval:
            StartInterval(self.plist_dict, self.config.interval.total_seconds()).generate_elements()
        ExitTimeOut(self.plist_dict, self.config.exittimeout).generate_elements()
        WorkingDirectory(
            self.plist_dict, os.path.expanduser(self.config.workingdir)
        ).generate_elements()
        StandardErrorPath(
            self.plist_dict, os.path.expanduser(os.path.join(LOGS_DIR, f"{self.full_job_name}.err"))
        ).generate_elements()
        StandardOutPath(
            self.plist_dict, os.path.expanduser(os.path.join(LOGS_DIR, f"{self.full_job_name}.out"))
        ).generate_elements()
        return self

    def write_plist(self) -> None:
        tree = etree.ElementTree(self.plist)
        with open(self.config.output_filepath(), "wb") as file:
            tree.write(
                file, pretty_print=True, xml_declaration=True, encoding="UTF-8", doctype=DOCTYPE
            )

    def print_plist(self) -> str:
        xml = etree.tostring(
            self.plist, pretty_print=True, xml_declaration=True, encoding="UTF-8", doctype=DOCTYPE
        )
        return xml.decode("utf-8")
