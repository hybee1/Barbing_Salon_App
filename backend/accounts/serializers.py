from rest_framework import serializers

from .models import ( User, CustomerProfile, StaffProfile,)

from .services import (create_customer, create_staff, update_user, update_staff_profile,
                       update_customer_profile, update_my_account, update_staff, )


class UserSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField( write_only=True, required=False, )

    class Meta:
        model = User

        fields = [
                    "id", "first_name", "last_name", "username", "email", "phone_number",
                    "password", "password2", "role", "image",
                    "is_active", "is_staff",
                    "is_superuser", "last_login", "date_joined",
                 ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },
        }

    def validate_phone_number(self, value):
        qs = User.objects.filter( phone_number=value, )

        if self.instance:
            qs = qs.exclude(  pk=self.instance.pk, )

        if qs.exists():
            raise serializers.ValidationError( "Phone number already exists." )

        return value

    def validate_email(self, value):
        qs = User.objects.filter( email=value, )

        if self.instance:
            qs = qs.exclude( pk=self.instance.pk, )

        if qs.exists():
            raise serializers.ValidationError( "Email already exists." )

        return value

    def validate_role(self, value):
        return User.Role.is_obj_of_role(value)

    def validate(self, attrs):

        password = attrs.get("password")
        password2 = attrs.get("password2")

        # ------------------------------------------------
        # Creation
        # ------------------------------------------------

        if self.instance is None:

            if not password:
                raise serializers.ValidationError({
                    "password":
                        "Password is required."
                })

            if not password2:
                raise serializers.ValidationError({
                    "password2":
                        "Password confirmation is required."
                })

            if password != password2:
                raise serializers.ValidationError({
                    "password2":
                        "Passwords do not match."
                })

        # ------------------------------------------------
        # Update
        # ------------------------------------------------

        elif password is not None:

            if not password2:
                raise serializers.ValidationError({
                    "password2":
                        "Password confirmation is required."
                })

            if password != password2:
                raise serializers.ValidationError({
                    "password2":
                        "Passwords do not match."
                })

        return attrs

    def create(self, validated_data):
        """
        User creation comes through the service layer.
        """

        role = validated_data.get("role")

        if role == User.Role.CUSTOMER:

            user, _ = create_customer( user_data=validated_data,  )

            return user

        elif role == User.Role.STAFF:

            user, _ = create_staff( user_data=validated_data, )

            return user

        elif role == User.Role.STAFF_ADMIN:

            # STAFF_ADMIN currently has no profile.
            #
            # Create the User directly, but still use
            # an atomic transaction through the service
            # layer.
            from django.db import transaction

            with transaction.atomic():

                password = validated_data.pop( "password", None, )

                user = User( **validated_data, )

                if password:
                    user.set_password(password)

                user.full_clean()
                user.save()

                return user

        raise serializers.ValidationError({
            "role": "Unsupported user role."
        })

    def update(self, instance, validated_data):
        """
        User updates come through the service layer.
        """

        return update_user(
            user=instance,
            user_data=validated_data,
        )


class UserForOthersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [ "id", "first_name", "last_name", "username",
                   "email", "phone_number", "role", "image", "is_active",
                   ]


class UserForOthersSerializer_2(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField( read_only=True, )

    class Meta:
        model = User

        fields = [
            "id", "first_name", "last_name", "full_name", "username",
            "email", "phone_number", "role", "image", "is_active",
            "date_joined", "last_login",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserForOthersSerializer_3(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "role",
            "image",
            "is_active",
        ]


class MiniUserDetailsSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField( source="get_full_name", read_only=True, )

    class Meta:
        model = User

        fields = [ "full_name", "username", "email", "phone_number",  "image", ]


class CustomerProfileSerializer(serializers.ModelSerializer):

    user = UserForOthersSerializer( read_only=True, )

    class Meta:
        model = CustomerProfile
        fields = "__all__"

    def update(self, instance, validated_data):

        return update_customer_profile(
            profile=instance,
            profile_data=validated_data,
        )


class StaffProfileSerializer(serializers.ModelSerializer):

    user = UserForOthersSerializer(
        read_only=True,
    )

    class Meta:
        model = StaffProfile
        fields = "__all__"

    def update(self, instance, validated_data):

        return update_staff_profile(
            profile=instance,
            profile_data=validated_data,
        )


class StaffProfileSerializer_2(serializers.ModelSerializer):

    user = UserForOthersSerializer_2(
        read_only=True,
    )

    class Meta:
        model = StaffProfile
        fields = "__all__"

    def update(self, instance, validated_data):

        return update_staff_profile(
            profile=instance,
            profile_data=validated_data,
        )


class StaffProfileSerializer_3(serializers.ModelSerializer):

    user = UserForOthersSerializer_3(
        read_only=True,
    )

    class Meta:
        model = StaffProfile
        fields = "__all__"

    def update(self, instance, validated_data):

        return update_staff_profile(
            profile=instance,
            profile_data=validated_data,
        )


class StaffProfileUserDetailsSerializer(serializers.ModelSerializer):

    user = MiniUserDetailsSerializer( read_only=True, )

    class Meta:
        model = StaffProfile
        fields = [ "user", ]


class StaffsWorkingTodaySerializer(serializers.ModelSerializer):

    user = MiniUserDetailsSerializer( read_only=True, )

    class Meta:
        model = StaffProfile
        fields = [ "user", ]


class StaffWriteSerializer(serializers.Serializer):
    """
    Used to create/update a Staff.

    Handles both User fields and StaffProfile fields.
    """

    # -------------------------
    # User fields
    # -------------------------

    first_name = serializers.CharField( required=False, allow_blank=True, )

    last_name = serializers.CharField( required=False, allow_blank=True, )

    username = serializers.CharField( required=False, )

    email = serializers.EmailField( required=False, )

    phone_number = serializers.CharField( required=False, )

    password = serializers.CharField( write_only=True, required=False, )

    password2 = serializers.CharField( write_only=True, required=False, )

    image = serializers.ImageField( required=False, allow_null=True, )

    is_active = serializers.BooleanField( default=True, required=False, )

    # -------------------------
    # StaffProfile fields
    # -------------------------

    department = serializers.ChoiceField(
                        choices=StaffProfile.Department.choices, required=True, )

    position = serializers.ChoiceField( choices=StaffProfile.Position.choices, required=True, )

    employment_date = serializers.DateField( required=True, )

    status = serializers.ChoiceField( choices=StaffProfile.StaffStatus.choices, required=True, )

    def validate_phone_number(self, value):

        qs = User.objects.filter( phone_number=value )

        if self.instance:
            qs = qs.exclude( pk=self.instance.user.pk )

        if qs.exists():
            raise serializers.ValidationError( "Phone number already exists." )

        return value

    def validate_email(self, value):

        qs = User.objects.filter( email=value )

        if self.instance:
            qs = qs.exclude( pk=self.instance.user.pk )

        if qs.exists():
            raise serializers.ValidationError( "Email already exists." )

        return value

    def validate(self, attrs):

        password = attrs.get("password")
        password2 = attrs.get("password2")

        # Creation
        if self.instance is None:

            if not password:
                raise serializers.ValidationError({ "password": "Password is required." })

            if password != password2:
                raise serializers.ValidationError({ "password2": "Passwords do not match." })

        # Update
        elif password is not None:

            if not password2:
                raise serializers.ValidationError(
                    { "password2": "Password confirmation is required." })

            if password != password2:
                raise serializers.ValidationError({ "password2": "Passwords do not match." })

        return attrs

    def create(self, validated_data):

        # Separate User fields from StaffProfile fields.
        staff_data = {
            "department": validated_data.pop(
                "department",
                StaffProfile.Department.BARBER,
            ),
            "position": validated_data.pop(
                "position",
                StaffProfile.Position.LEVEL_ONE,
            ),
            "employment_date": validated_data.pop(
                "employment_date",
            ),
            "status": validated_data.pop(
                "status",
                StaffProfile.StaffStatus.ACTIVE,
            ),
        }

        user, staff = create_staff(
            user_data=validated_data,
            staff_data=staff_data,
        )

        return staff

    def update(self, instance, validated_data):

        staff_data = {}

        for field in (
            "department",
            "position",
            "employment_date",
            "status",
        ):
            if field in validated_data:
                staff_data[field] = validated_data.pop(field)

        user_data = validated_data

        user, staff = update_staff(
            staff=instance,
            user_data=user_data,
            staff_data=staff_data,
        )

        return staff

    def to_representation(self, instance):
        return StaffProfileSerializer_2(instance).data

# former class BarberSelfUpdateSerializer(serializers.ModelSerializer):
class AllStaff_Self_UpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for the currently authenticated barber.

    A staff can update their own:
        - first_name
        - last_name
        - username
        - email
        - phone_number
        - image
        - password

    A barber cannot change:
        - role
        - is_staff
        - is_superuser
        - is_active
        - date_joined
        - last_login
    """

    current_password = serializers.CharField(  write_only=True, required=False, )

    password = serializers.CharField(  write_only=True, required=False,  )

    password2 = serializers.CharField( write_only=True, required=False, )

    class Meta:
        model = User

        fields = [
            "first_name", "last_name", "username", "email", "phone_number",
            "image", "current_password", "password", "password2",
        ]

    def validate_username(self, value):
        value = value.strip()

        qs = User.objects.filter( username__iexact=value, ).exclude( pk=self.instance.pk,  )

        if qs.exists():
            raise serializers.ValidationError( "Username already exists." )

        return value

    def validate_email(self, value):
        value = value.strip()

        qs = User.objects.filter( email__iexact=value, ).exclude( pk=self.instance.pk, )

        if qs.exists():
            raise serializers.ValidationError( "Email already exists." )

        return value

    def validate_phone_number(self, value):
        qs = User.objects.filter( phone_number=value, ).exclude( pk=self.instance.pk, )

        if qs.exists():
            raise serializers.ValidationError( "Phone number already exists." )

        return value

    def validate(self, attrs):

        password = attrs.get("password")
        password2 = attrs.get("password2")
        current_password = attrs.get("current_password")

        # -----------------------------------------
        # Password is being changed
        # -----------------------------------------

        if password is not None:

            if not current_password:
                raise serializers.ValidationError(
                    {
                    "current_password": "Current password is required."  }
                )

            if not password2:
                raise serializers.ValidationError(
                    { "password2": "Password confirmation is required." }
                )

            if password != password2:
                raise serializers.ValidationError(
                    { "password2": "Passwords do not match." }
                )

        # Don't allow password2 without password.
        elif password2 is not None:

            raise serializers.ValidationError(
                { "password": "Password is required when confirming a password." }
            )

        return attrs

    def update(self, instance, validated_data):

        current_password = validated_data.pop( "current_password", None, )

        return update_my_account(
            user=instance,
            user_data=validated_data,
            current_password=current_password,
        )