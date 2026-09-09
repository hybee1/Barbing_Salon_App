
# backend/accounts/authentication.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


User = get_user_model()



class Auth_Using_UsernameOrPhone(ModelBackend):

    def authenticate( self, request, username_or_phone=None, password=None, **kwargs):
        if not username_or_phone or not password:
            return None

        user = (
            User.objects.filter(
                Q(username__iexact=username_or_phone) | Q(phone_number=username_or_phone) ).first()
        )

        if user is None:
            return None

        if not user.check_password(password):
            return None

        if not self.user_can_authenticate(user):
            return None

        return user
