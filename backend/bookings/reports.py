
from django.db.models import Count, Sum, F
from django.utils import timezone
from .models import Booking

# CLASS
class ReportService:
    """
    Handles all business analytics.
    """

    @staticmethod
    def today_summary():
        today = timezone.now().date()

        bookings = Booking.objects.filter(
            booking_date=today
        )

        return {
            "total_bookings": bookings.count(),
            "completed": bookings.filter(status="COMPLETED").count(),
            "cancelled": bookings.filter(status="CANCELLED").count(),
            "no_show": bookings.filter(status="NO_SHOW").count(),
        }

    # Revenue Report
    # We assume:
    # Revenue = service price
    # Only COMPLETED bookings count
    @staticmethod
    def today_revenue():
        today = timezone.now().date()

        revenue = Booking.objects.filter(
            booking_date=today,
            status="COMPLETED"
        ).aggregate(
            total=Sum("service__price")
        )["total"]

        return {
            "revenue": revenue or 0
        }

    # MOST POPULAR SERVICE
    @staticmethod
    def popular_services():
        return Booking.objects.values(
            "service__name"
        ).annotate(
            total=Count("id")
        ).order_by("-total")[:5]

    # TOP STAFF
    @staticmethod
    def top_staff():
        return Booking.objects.filter(
            status="COMPLETED"
        ).values(
            "staff__full_name"
        ).annotate(
            total=Count("id")
        ).order_by("-total")[:5]

    # NO SHOW RATE
    @staticmethod
    def no_show_rate():
        total = Booking.objects.count()

        no_shows = Booking.objects.filter(
            status="NO_SHOW"
        ).count()

        if total == 0:
            return 0

        return round((no_shows / total) * 100, 2)
