from __future__ import annotations

import os
import subprocess

from macschedule.job_configs import JobConfig


class PListLoader:
    """Load and unload job using `launchctl` given a `JobConfig`."""

    def __init__(self, config: JobConfig) -> None:
        self.config = config

    def load(self) -> None:
        if not os.path.exists(self.config.output_filepath()):
            raise ValueError("Missing .plist file. Try running `msch generate` first.")
        proc = subprocess.run(
            ["launchctl", "load", self.config.output_filepath()],
            capture_output=True,
        )
        err = proc.stderr.decode("utf-8").strip()
        if err:
            raise ValueError(err)

    def unload(self) -> None:
        proc = subprocess.run(
            ["launchctl", "unload", self.config.output_filepath()],
            capture_output=True,
        )
        err = proc.stderr.decode("utf-8").strip()
        if err:
            raise ValueError(err)
