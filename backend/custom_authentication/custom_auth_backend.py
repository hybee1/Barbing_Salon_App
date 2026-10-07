from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


User = get_user_model()


class Auth_Using_UsernameOrPhone(ModelBackend):

    def authenticate( self, request, username=None, password=None, username_or_phone=None, **kwargs ):

        identifier = username_or_phone or username

        if not identifier or not password:
            return None

        user = (
            User.objects .filter( Q(username__iexact=identifier) | Q(phone_number=identifier) ).first()
        )

        if user is None:

            return None

        if not user.check_password(password):
            return None

        if not self.user_can_authenticate(user):
            return None

        return user
