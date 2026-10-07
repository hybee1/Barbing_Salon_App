
from datetime import timezone as dt_timezone, datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from rest_framework.exceptions import ValidationError

from backend.accounts.models import StaffProfile
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.salon_settings.services_salon_config import get_salon_info_config
from backend.utils.services import convert_utc_iso_to_salon_time


@transaction.atomic
def create_break_period(*, staff_id, break_start_date_time_in_salon_tz,
                        break_end_date_time_in_salon_tz, status, reason):

    if break_start_date_time_in_salon_tz.tzinfo is None:
        raise ValidationError({
            "break_start_date_time": "Datetime must be timezone-aware."
        })

    if break_end_date_time_in_salon_tz.tzinfo is None:
        raise ValidationError({
            "break_end_date_time": "Datetime must be timezone-aware."
        })

    if break_start_date_time_in_salon_tz >= break_end_date_time_in_salon_tz:
        raise ValidationError({
            "details": "Break end time must be after start time."
        })

    # convert the start and end time to utc time
    break_start_date_time_utc = break_start_date_time_in_salon_tz.astimezone(dt_timezone.utc)
    break_end_date_time_utc = break_end_date_time_in_salon_tz.astimezone(dt_timezone.utc)
    break_date_in_salon_tz = break_start_date_time_in_salon_tz.date()

    # Lock this staff for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    staff = ( StaffProfile.objects.select_for_update().get(pk=staff_id) )

    # Overlap validation
    overlap = BreakTimeAndOffDays.objects.filter(
        staff=staff,
        # break_date=selected_date,
        break_start_date_time__lt=break_end_date_time_utc,
        break_end_date_time__gt=break_start_date_time_utc,
    )

    if overlap.exists():
        raise ValidationError({
            "details": "This availability block overlaps with an existing one."})


    break_period = BreakTimeAndOffDays( staff=staff, break_date=break_date_in_salon_tz,
                                   break_start_date_time=break_start_date_time_utc,
                                   break_end_date_time=break_end_date_time_utc,
                                   status=status, reason=reason )

    # break_period.full_clean()
    break_period.save()
    return break_period


def break_time_and_offDays_data_with_timezone(*, data: dict | list[dict]) -> dict | list[dict]:
    salon_info = get_salon_info_config()
    salon_timezone = ZoneInfo(salon_info["time_zone"])

    if not isinstance(data, (dict, list)):
        raise ValidationError({"details": "invalid booking data. booking data "
                                          "is either a dict or a list of dict"})

    if isinstance(data, dict):
        if "break_date" not in data:
            raise ValidationError({"details": "A booking 'date' is required."})

        if "break_start_date_time" not in data:
            raise ValidationError({"details": "A booking 'break_start_date_time' is required."})
        break_start_date_time_str = data['break_start_date_time']

        if "break_end_date_time" not in data:
            raise ValidationError({"details": "A booking 'break_end_date_time' is required."})
        break_end_date_time_str = data['break_end_date_time']

        break_date_start_time = convert_utc_iso_to_salon_time(break_start_date_time_str, salon_timezone)

        break_date_end_time = convert_utc_iso_to_salon_time(break_end_date_time_str, salon_timezone)

        data['start_date'] = break_date_start_time.date()
        data['end_date'] = break_date_end_time.date()

        data['start_time'] = break_date_start_time.time()
        data['end_time'] = break_date_end_time.time()

        return data

    elif isinstance(data, list):

        res_list: list[dict] = []
        for item in data:

            if not isinstance(item, dict):
                raise ValidationError({
                    "details": "Each item in booking data must be a dictionary."
                })

            if "break_date" not in item:
                raise ValidationError({"details": "A booking 'date' is required."})

            if "break_start_date_time" not in item:
                raise ValidationError({"details": "A booking 'break_start_date_time' is required."})
            break_start_date_time_str = item['break_start_date_time']

            if "break_end_date_time" not in item:
                raise ValidationError({"details": "A booking 'break_end_date_time' is required."})
            break_end_date_time_str = item['break_end_date_time']

            break_date_start_time = convert_utc_iso_to_salon_time(break_start_date_time_str, salon_timezone)

            break_date_end_time = convert_utc_iso_to_salon_time(break_end_date_time_str, salon_timezone)

            item['start_date'] = break_date_start_time.date()
            item['end_date'] = break_date_end_time.date()

            item['start_time'] = break_date_start_time.time()
            item['end_time'] = break_date_end_time.time()

            res_list.append(item)

        return res_list