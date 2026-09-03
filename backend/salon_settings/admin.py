
from django.contrib import admin
from django import forms


from .models import SalonInfo, SalonBookingSetting
from .services_salon_config import normalize_country, normalize_phone_number
from ..exceptions.exceptions import InvalidPhoneNumberError, InvalidCountryError


class SalonInfoAdminForm(forms.ModelForm):

    class Meta:
        model = SalonInfo
        fields = "__all__"

    def clean_salon_country(self):
        value = self.cleaned_data["salon_country"]

        try:
            return normalize_country(value)
        except InvalidCountryError as exc:
            raise forms.ValidationError(str(exc))

    def clean_salon_phone_number(self):
        value = self.cleaned_data["salon_phone_number"]

        country = self.cleaned_data.get("salon_country")

        if not country:
            raise forms.ValidationError(
                "Country is required to validate the phone number."
            )

        try:
            return normalize_phone_number( value=value, country=country,  )
        except ( InvalidCountryError, InvalidPhoneNumberError, ) as exc:
            raise forms.ValidationError(str(exc))


@admin.register(SalonInfo)
class SalonInfoAdmin(admin.ModelAdmin):

    form = SalonInfoAdminForm

    list_display = ( "salon_name", "salon_email", "salon_time_zone", "salon_currency",
                      "salon_open_time", "salon_close_time", "salon_phone_number",
                     "salon_country", "salon_address",
                     # "created_at", "updated_at",
    )

    search_fields = ( "salon_name", "salon_address",  "salon_phone_number", )

    list_filter = ( "salon_country", "salon_time_zone", "salon_currency", )


@admin.register(SalonBookingSetting)
class SalonBookingSettingAdmin(admin.ModelAdmin):

    list_display = ( "booking_slot_interval", "allow_online_booking",
                     # "created_at", "updated_at",
                     )
    list_filter = ("allow_online_booking",)
