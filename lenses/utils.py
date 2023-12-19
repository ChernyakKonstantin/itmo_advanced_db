from datetime import datetime, timedelta


def get_end_ts(start_ts: datetime, duration: timedelta) -> datetime:
    return start_ts + duration
