from datetime import datetime

import pytz


def naive_to_utc_dt(naive_dt: datetime, timezone):
    local_dt = timezone.localize(naive_dt, is_dst=None)
    return local_dt.astimezone(pytz.utc).replace(tzinfo=None)


def utc_to_local_dt(utc_dt: datetime, timezone):
    return utc_dt.astimezone(timezone)
