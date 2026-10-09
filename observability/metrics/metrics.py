
from prometheus_client import Counter, Histogram


BOOKINGS_CREATED = Counter(
    "bookings_created_total",
    "Total number of bookings created",
)


BOOKING_STATUS_CHANGED = Counter(
    "booking_status_changed_total",
    "Total booking status changes",
    [
        "old_status",
        "new_status",
    ],
)


BOOKING_STATUS_CHANGE_REJECTED = Counter(
    "booking_status_change_rejected_total",
    "Total rejected booking status changes",
    [
        "reason",
        "requested_status",
    ],
)


BOOKING_OPERATION_DURATION = Histogram(
    "booking_operation_duration_seconds",
    "Time spent processing booking operations",
    [
        "operation",
    ],
)