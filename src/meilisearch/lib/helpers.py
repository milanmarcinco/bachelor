import datetime


def now():
    timestamp = datetime.datetime.now().isoformat()
    return f"[{timestamp}]"
