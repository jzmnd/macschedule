from itertools import product
from typing import List

from cron_converter import Cron

from macschedule.job_configs import Schedule


def cron_to_schedules(cron: str) -> List[Schedule]:
    """Convert a standard cron string to a list of `Schedule` objects.

    In simple cases such as `5 0 3 * *` (00:05 every 3rd day of month) only one `Schedule`
    object is required to represent this:

        `Schedule(minute=5, hour=0, day=3, month=None, weekday=None)`

    However, for more complicated cron string that include multiple values such as `5 0 3,18 * *`
    (00:05 every 3rd and 18th day of month) multiple `Schedule` objects must be created:

        `Schedule(minute=5, hour=0, day=3, month=None, weekday=None)`
        `Schedule(minute=5, hour=0, day=18, month=None, weekday=None)`

    The function uses itertools.product to get all the combinations of time periods in this case.
    """
    cron_c = Cron(cron)
    non_full_parts = {part.unit["name"]: part.values for part in cron_c.parts if not part.is_full()}
    return [
        Schedule(**dict(zip(non_full_parts.keys(), part_vals)))
        for part_vals in product(*non_full_parts.values())
    ]
