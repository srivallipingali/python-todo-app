from datetime import datetime

DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M"


def is_valid_date(value):
    if not value:
        return True
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        return False
    return True


def is_valid_time(value):
    if not value:
        return True
    try:
        datetime.strptime(value, TIME_FORMAT)
    except ValueError:
        return False
    return True


def has_valid_deadline(due_date, end_time):
    return is_valid_date(due_date) and is_valid_time(end_time) and bool(
        due_date or not end_time
    )
