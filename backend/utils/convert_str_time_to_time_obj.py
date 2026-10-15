from datetime import datetime, time


def convert_to_time(time_string: str) -> time:
    formats = ["%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"]

    for fmt in formats:
        try:
            return datetime.strptime(time_string, fmt).time()
        except ValueError:
            continue

    raise ValueError(f"Unsupported time format: {time_string!r}")