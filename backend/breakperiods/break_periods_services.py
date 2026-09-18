from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError

from backend.accounts.models import StaffProfile
from backend.breakperiods.models import BreakTimeAndOffDays
from backend.salon_settings.services_salon_config import get_salon_info_config


@transaction.atomic
def create_break_period( *, staff_id, break_start_date_time, break_end_date_time, status, reason):

    # convert the start and end time to utc time
    break_start_date_time_utc = break_start_date_time.astimezone(ZoneInfo(settings.TIME_ZONE))
    break_end_date_time_utc = break_end_date_time.astimezone(ZoneInfo(settings.TIME_ZONE))
    break_date = break_start_date_time

    # Lock this staff for the duration of the transaction.
    # Any other booking attempt for this same barber must wait.
    staff = ( StaffProfile.objects.select_for_update().get(pk=staff_id) )


    booking = BreakTimeAndOffDays( staff=staff, break_date=break_date,
                                   break_start_date_time=break_start_date_time_utc,
                                   break_end_date_time=break_end_date_time_utc,
                                   status=status, reason=reason )

    booking.full_clean()
    booking.save()
    return booking


def break_time_and_offDays_data_with_timezone(*, data: dict | list[dict]) -> dict | list[dict]:
    salon_info = get_salon_info_config()
    salon_timezone = salon_info.timezone

    if not isinstance(data, (dict, list[dict])):
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

        break_date_start_time = break_start_date_time_str.astimezone(salon_timezone)
        break_date_end_time = break_end_date_time_str.astimezone(salon_timezone)

        data['start_time'] = break_date_start_time.time()
        data['end_time'] = break_date_end_time.time()

        return data

    elif isinstance(data, list):

        res_list: list[dict] = []
        for item in data:
            if "break_date" not in item:
                raise ValidationError({"details": "A booking 'date' is required."})
            break_date_str = item['break_date']

            if "break_start_date_time" not in item:
                raise ValidationError({"details": "A booking 'break_start_date_time' is required."})
            break_start_date_time_str = item['break_start_date_time']

            if "break_end_date_time" not in item:
                raise ValidationError({"details": "A booking 'break_end_date_time' is required."})
            break_end_date_time_str = item['break_end_date_time']

            break_date_start_time = break_start_date_time_str.astimezone(salon_timezone)
            break_date_end_time = break_end_date_time_str.astimezone(salon_timezone)

            item['start_time'] = break_date_start_time.time()
            item['end_time'] = break_date_end_time.time()

            res_list.append(item)

        return res_list