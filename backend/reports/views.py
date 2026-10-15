# ==========================================================
# views.py
# Levelz Cuts - Manager Reports
# ==========================================================

from datetime import timedelta, datetime, timezone as dt_timezone, date
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import (
    Count,
    Sum,
    DecimalField,
    F,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response

from backend.bookings.models import Booking
from backend.custom_permissions.permissions import IsSalonManager
from backend.inventory.models import InventoryItem
from backend.salon_settings import services_salon_config
import re

# ==========================================================
# HELPERS
# ==========================================================

MONEY_FIELD = DecimalField( max_digits=12, decimal_places=2, )

def parse_report_date(value, field_name):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(
            f"{field_name} must use YYYY-MM-DD format."
        )

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid calendar date."
        ) from exc


def get_completed_bookings():

    return Booking.objects.filter( status=Booking.STATUS.COMPLETED )


def get_booking_summary(queryset):

    return {

        "total": queryset.count(),

        "confirmed": queryset.filter(
            status=Booking.STATUS.CONFIRMED
        ).count(),

        "arrived": queryset.filter(
            status=Booking.STATUS.ARRIVED
        ).count(),

        "in_progress": queryset.filter(
            status=Booking.STATUS.IN_PROGRESS
        ).count(),

        "completed": queryset.filter(
            status=Booking.STATUS.COMPLETED
        ).count(),

        "cancelled": queryset.filter(
            status=Booking.STATUS.CANCELLED
        ).count(),

        "no_show": queryset.filter(
            status=Booking.STATUS.NO_SHOW
        ).count(),

    }


def get_low_stock_count():

    return InventoryItem.objects.filter(
        status=InventoryItem.Status.ACTIVE,
        quantity__lte=F("reorder_level")
    ).count()


def get_staff_performance(queryset):

    staff_queryset = (

        queryset

        .values(
            "barber__user__first_name",
            "barber__user__last_name",
            "barber__user__username",
        )

        .annotate(

            booking_count=Count("id"),

            revenue=Coalesce(
                Sum("price"),
                Decimal("0.00"),
                output_field=MONEY_FIELD,
            ),

        )

        .order_by(
            "-booking_count",
            "-revenue",
        )

    )


    staff = []


    for member in staff_queryset:

        first_name = (
            member[
                "barber__user__first_name"
            ]
            or ""
        )


        last_name = (
            member[
                "barber__user__last_name"
            ]
            or ""
        )


        full_name = (
            f"{first_name} {last_name}"
        ).strip()


        staff_name = (

            full_name

            or member[
                "barber__user__username"
            ]

            or "Unknown Staff"

        )


        staff.append({

            "staff_name":
                staff_name,

            "booking_count":
                member["booking_count"],

            "revenue":
                member["revenue"],

        })


    return staff


def get_service_performance(queryset):

    return list(

        queryset.values( "service__name" )

        .annotate( booking_count=Count("id"),

            revenue=Coalesce(
                Sum("price"),
                Decimal("0.00"),
                output_field=MONEY_FIELD,
            ),

        )

        .order_by( "-booking_count", "-revenue", )[:10]

    )


# ==========================================================
# GROUPING
# ==========================================================

def determine_report_grouping( start_date, end_date):

    days = ( end_date - start_date  ).days + 1


    if days <= 31:

        return "day"


    if days <= 90:

        return "week"


    return "month"


# ==========================================================
# WEEK START
# ==========================================================

def get_week_start(date1) -> date:

    return date1 - timedelta( days=date1.weekday() )


# ==========================================================
# TREND DATA
# ==========================================================

def build_daily_trend( bookings: Booking, start_date_in_salon_tz: date, end_date_in_salon_tz: date ):

    if start_date_in_salon_tz > end_date_in_salon_tz:
        raise ValueError({ "detail": "Start date must not be after end date."})

    salon_info = services_salon_config.get_salon_info_config()
    salon_open_time = salon_info["open_time"]
    salon_close_time = salon_info["close_time"]
    salon_tz = ZoneInfo(salon_info["time_zone"])

    trend = []

    current_date = start_date_in_salon_tz

    while current_date <= end_date_in_salon_tz:
        # salon open hours
        current_date_time_open_hours_in_utc = datetime.combine(current_date, salon_open_time,
                                                               tzinfo=salon_tz).astimezone(dt_timezone.utc)

        # salon close hours
        current_date_time_close_hours_in_utc = datetime.combine(current_date, salon_close_time,
                                                                tzinfo=salon_tz).astimezone(dt_timezone.utc)

        day_bookings = bookings.filter(session_start_date_time__gte=current_date_time_open_hours_in_utc,
            session_start_date_time__lt=current_date_time_close_hours_in_utc,)

        completed = day_bookings.filter( status=Booking.STATUS.COMPLETED )

        revenue = completed.aggregate(

            total=Coalesce(
                Sum("price"), Decimal("0.00"), output_field=MONEY_FIELD, )

        )["total"]

        total = day_bookings.count()

        completed_count = completed.count()

        completion_rate = ( ( completed_count / total ) * 100 if total else 0 )


        trend.append({

            "period": current_date.isoformat(),

            "period_label": current_date.strftime( "%d %b" ),

            "bookings": total,

            "completed": completed_count,

            "revenue": revenue,

            "completion_rate": round( completion_rate, 2 ),

        })

        current_date += timedelta( days=1 )

    return trend


def build_weekly_trend( bookings: Booking, start_date_in_salon_tz: date, end_date_in_salon_tz: date ):

    if start_date_in_salon_tz > end_date_in_salon_tz:
        raise ValueError({ "detail": "Start date must not be after end date."})

    salon_info = services_salon_config.get_salon_info_config()
    salon_open_time = salon_info["open_time"]
    salon_close_time = salon_info["close_time"]
    salon_tz = ZoneInfo(salon_info["time_zone"])

    trend = []

    # the current_week_start_day is either monday which is the start of that week
    current_week_start_day = get_week_start( start_date_in_salon_tz )

    # the last_week_start_day is either monday which is the start of that week
    last_week_start_day = get_week_start( end_date_in_salon_tz  )

    while current_week_start_day <= last_week_start_day:

        week_end = current_week_start_day + timedelta( days=6 )

        range_start = max( current_week_start_day, start_date_in_salon_tz )

        range_end = min( week_end, end_date_in_salon_tz )

        # salon open hours
        range_start_date_time_open_hours_in_utc = datetime.combine(range_start, salon_open_time,
                                                               tzinfo=salon_tz).astimezone(dt_timezone.utc)

        # salon close hours
        # range_end_date_time_close_hours_in_utc = datetime.combine(range_end + timedelta(days=1),
        #                                                           salon_close_time,
        #                                                         tzinfo=salon_tz).astimezone(dt_timezone.utc)

        range_end_date_time_close_hours_in_utc = datetime.combine(range_end,
                                                                  salon_close_time,
                                                                  tzinfo=salon_tz).astimezone(dt_timezone.utc)

        week_bookings = bookings.filter(
            session_start_date_time__gte=range_start_date_time_open_hours_in_utc,
            session_start_date_time__lt=range_end_date_time_close_hours_in_utc,
        )


        completed = week_bookings.filter( status=Booking.STATUS.COMPLETED  )

        revenue = completed.aggregate(
            total=Coalesce( Sum("price"), Decimal("0.00"), output_field=MONEY_FIELD, )

        )["total"]

        total = week_bookings.count()

        completed_count = completed.count()

        completion_rate = ( ( completed_count / total ) * 100 if total else 0  )

        trend.append({

            "period": current_week_start_day.isoformat(),

            "period_label":
                (
                    f"{range_start.strftime('%d %b')}"
                    f" - "
                    f"{range_end.strftime('%d %b')}"
                ),

            "bookings": total,

            "completed": completed_count,

            "revenue": revenue,

            "completion_rate": round( completion_rate, 2 ),

        })

        current_week_start_day += timedelta( days=7 )

    return trend


def build_monthly_trend( bookings: Booking, start_date_in_salon_tz: date, end_date_in_salon_tz: date  ):

    if start_date_in_salon_tz > end_date_in_salon_tz:
        raise ValueError({"details": "Start date must not be after end date."})

    salon_info = services_salon_config.get_salon_info_config()
    salon_tz = ZoneInfo(salon_info["time_zone"])
    salon_open_time = salon_info["open_time"]
    salon_close_time = salon_info["close_time"]

    trend = []

    current_date = start_date_in_salon_tz.replace(day=1)

    while current_date <= end_date_in_salon_tz:

        # Calculate the first day of the next month.
        if current_date.month == 12:
            next_month = current_date.replace( year=current_date.year + 1, month=1, day=1, )
        else:
            next_month = current_date.replace( month=current_date.month + 1, day=1, )

        # Last calendar day of the current month.
        month_end = next_month - timedelta(days=1)

        # Restrict the first and last months to the requested date range.
        range_start = max(current_date, start_date_in_salon_tz)
        range_end = min(month_end, end_date_in_salon_tz)

        # Convert salon-local calendar boundaries to UTC.
        start_local = datetime.combine( range_start, salon_open_time, tzinfo=salon_tz, )

        # end_local = datetime.combine( range_end + timedelta(days=1), salon_close_time, tzinfo=salon_tz )
        end_local = datetime.combine(range_end, salon_close_time, tzinfo=salon_tz, )

        start_utc = start_local.astimezone(dt_timezone.utc)
        end_utc = end_local.astimezone(dt_timezone.utc)

        month_bookings = bookings.filter(
            session_start_date_time__gte=start_utc,
            session_start_date_time__lt=end_utc,
        )

        completed = month_bookings.filter( status=Booking.STATUS.COMPLETED, )

        revenue = completed.aggregate(
            total=Coalesce(
                Sum("price"),
                Decimal("0.00"),
                output_field=MONEY_FIELD,
            )
        )["total"]

        total = month_bookings.count()
        completed_count = completed.count()

        completion_rate = ( completed_count / total * 100 if total else 0 )

        trend.append({
            "period": current_date.strftime("%Y-%m"),
            "period_label": current_date.strftime("%b %Y"),
            "bookings": total,
            "completed": completed_count,
            "revenue": revenue,
            "completion_rate": round(completion_rate, 2),
        })

        current_date = next_month

    return trend


def build_report_trend( bookings, start_date,  end_date, grouping ):

    if grouping == "month":

        return build_monthly_trend( bookings, start_date, end_date )

    if grouping == "week":

        return build_weekly_trend( bookings, start_date, end_date )

    return build_daily_trend( bookings, start_date, end_date )


# ==========================================================
# MAIN MANAGER REPORT
# ==========================================================

class ManagerReportView(APIView):

    permission_classes = [IsSalonManager]

    def get( self, request):

        salon_info = services_salon_config.get_salon_info_config()
        salon_tz = ZoneInfo(salon_info["time_zone"])
        salon_open_time = salon_info["open_time"]
        salon_close_time = salon_info["close_time"]

        today_date_time_utc = timezone.now()

        start_today_date_time_in_salon_tz = today_date_time_utc.astimezone(salon_tz)
        today_date_in_salon_tz = start_today_date_time_in_salon_tz.date()

        start_today_date_time_in_salon_tz = datetime.combine(
                            today_date_in_salon_tz, salon_open_time, tzinfo=salon_tz, )

        end_today_date_time_in_salon_tz = datetime.combine(
                            today_date_in_salon_tz, salon_close_time, tzinfo=salon_tz, )

        start_today_date_time_in_utc = start_today_date_time_in_salon_tz.astimezone(dt_timezone.utc)

        end_today_date_time_in_utc = end_today_date_time_in_salon_tz.astimezone(dt_timezone.utc)

        bookings = Booking.objects.all()


        completed_bookings = get_completed_bookings()

        booking_summary = get_booking_summary( bookings )

        today_revenue = ( completed_bookings .filter( session_start_date_time__range=(
                                start_today_date_time_in_utc, end_today_date_time_in_utc)
        ).aggregate(

                total=Coalesce(
                    Sum("price"),
                    Decimal("0.00"),
                    output_field=MONEY_FIELD,
                )

            )["total"]

        )

        services = get_service_performance( completed_bookings )

        staff = get_staff_performance( completed_bookings  )

        low_stock_count = get_low_stock_count()

        return Response({

            "bookings": booking_summary,

            "revenue": { "today": today_revenue,  },

            "services": services,

            "staff": staff,

            "inventory": { "low_stock_count": low_stock_count, },

        })


# ==========================================================
# DATE RANGE REPORT
# ==========================================================

class ManagerDateRangeReportView(APIView):

    permission_classes = [IsSalonManager]


    def get( self, request, ):

        # --------------------------------------------------
        # QUERY PARAMETERS
        # --------------------------------------------------

        start_date_param = request.query_params.get( "start_date" )

        end_date_param = request.query_params.get( "end_date" )

        salon_info = services_salon_config.get_salon_info_config()
        salon_tz = ZoneInfo(salon_info["time_zone"])
        salon_open_time = salon_info["open_time"]
        salon_close_time = salon_info["close_time"]

        # Always use date objects for report periods.
        today_date_time_in_utc = timezone.now()
        today_date_in_salon_tz = today_date_time_in_utc.astimezone(salon_tz).date()

        # --------------------------------------------------
        # START DATE
        # --------------------------------------------------
        try:
            start_date = ( parse_report_date(start_date_param, "start_date")
                           if start_date_param else today_date_in_salon_tz
            )
        except ValueError as exc:
            return Response(
                # {"detail": "start_date must use YYYY-MM-DD format."},
                {"detail": str(exc)},
                status=400,
            )

        # --------------------------------------------------
        # END DATE
        # --------------------------------------------------
        try:
            end_date = ( parse_report_date(end_date_param, "end_date")
                         if end_date_param else today_date_in_salon_tz
            )
        except ValueError as exc:
            return Response(
                # {"detail": "end_date must use YYYY-MM-DD format."},
                {"detail": str(exc)},
                status=400,
            )

        # --------------------------------------------------
        # VALIDATE
        # --------------------------------------------------

        if start_date> end_date:

            return Response(
                { "detail": "start_date cannot be after end_date." },
                status=400
            )

        # --------------------------------------------------
        # CONVERT SALON-LOCAL BUSINESS HOURS TO UTC
        # --------------------------------------------------
        start_date_utc = datetime.combine(
                                start_date, salon_open_time, tzinfo=salon_tz, ).astimezone(dt_timezone.utc)

        end_date_utc = datetime.combine(
                            end_date, salon_close_time, tzinfo=salon_tz, ).astimezone(dt_timezone.utc)

        # --------------------------------------------------
        # BOOKINGS
        # --------------------------------------------------
        bookings = Booking.objects.filter(
            session_start_date_time__gte=start_date_utc,
            session_start_date_time__lt=end_date_utc,
        )

        completed_bookings = bookings.filter( status=Booking.STATUS.COMPLETED )

        booking_summary = get_booking_summary( bookings )


        # --------------------------------------------------
        # REVENUE
        # --------------------------------------------------

        revenue = completed_bookings.aggregate(

                total=Coalesce(
                    Sum("price"),
                    Decimal("0.00"),
                    output_field=MONEY_FIELD,
                )

            )["total"]


        # --------------------------------------------------
        # COMPLETION RATE
        # --------------------------------------------------

        total_bookings = booking_summary["total"]


        completed_count = booking_summary["completed"]


        completion_rate = ( ( completed_count / total_bookings ) * 100 if total_bookings else 0 )

        # --------------------------------------------------
        # SERVICES
        # --------------------------------------------------

        services = get_service_performance( completed_bookings )

        # --------------------------------------------------
        # STAFF
        # --------------------------------------------------

        staff = get_staff_performance( completed_bookings )

        # --------------------------------------------------
        # GROUPING
        # --------------------------------------------------

        grouping = determine_report_grouping( start_date, end_date )

        # --------------------------------------------------
        # TREND
        # --------------------------------------------------

        trend = build_report_trend( bookings, start_date, end_date, grouping )

        # --------------------------------------------------
        # INVENTORY
        # --------------------------------------------------

        low_stock_count = get_low_stock_count()

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return Response({

            "start_date": start_date.isoformat(),

            "end_date": end_date.isoformat(),

            "grouping": grouping,

            "bookings": booking_summary,

            "revenue": { "total":  revenue, },

            "completion_rate": round( completion_rate, 2 ),

            "trend": trend,

            "services": services,

            "staff": staff,

            "inventory": { "low_stock_count": low_stock_count, },

        })
