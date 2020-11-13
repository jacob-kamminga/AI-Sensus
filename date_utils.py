from datetime import datetime

import pytz


def naive_to_utc(naive_dt: datetime, timezone):
    local_dt = timezone.localize(naive_dt, is_dst=None)
    return local_dt.astimezone(pytz.utc).replace(tzinfo=None)


def utc_to_local(utc_dt, local_tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

