
from django.db.models import Q, OuterRef, Exists
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework.response import Response
from rest_framework.views import APIView

from backend.accounts.models import User, StaffProfile
from backend.accounts.serializers import StaffProfileSerializer, StaffProfileUserDetailsSerializer, \
    StaffsWorkingTodaySerializer, StaffProfileSerializer_2,  StaffWriteSerializer, \
    AllStaff_Self_UpdateSerializer
from backend.accounts.services import delete_staff
from backend.breakperiods.models import BreakTimeAndOffDays

from rest_framework_simplejwt.views import TokenRefreshView

from backend.custom_permissions.permissions import Is_Authenticated_Staff_User, Is_SalonManager
from backend.pagination.pagination import StandardResultsSetPagination


class Barbers_Web_View(APIView):

    def get(self, request, pk=None):

        # -----------------------------------------
        # Get a specific barber
        # -----------------------------------------

        if pk is not None:

            barber = (
                StaffProfile.objects.select_related("user")
                .filter(
                    pk=pk,
                    user__role=User.Role.STAFF,
                    department=StaffProfile.Department.BARBER,
                )
                .first()
            )

            if barber is None:
                return Response(
                    {
                        "detail": "Barber not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = StaffProfileSerializer(
                barber
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        # -----------------------------------------
        # List barbers
        # -----------------------------------------

        barbers = (
            StaffProfile.objects
            .select_related("user")
            .filter(
                user__role=User.Role.STAFF,
                department=StaffProfile.Department.BARBER,
            )
        )

        serializer = StaffProfileSerializer( barbers, many=True, )

        return Response( serializer.data, status=status.HTTP_200_OK, )


class Barbers_Api_View(APIView):

    permission_classes = [ Is_Authenticated_Staff_User, ]

    parser_classes = [ MultiPartParser, FormParser, JSONParser, ]

    def get(self, request, pk=None):

        # -----------------------------------------
        # Get a specific barber
        # -----------------------------------------

        if pk is not None:

            barber = (
                StaffProfile.objects.select_related("user")
                .filter(
                    pk=pk,
                    user__role=User.Role.STAFF,
                    department=StaffProfile.Department.BARBER,
                )
                .first()
            )

            if barber is None:
                return Response(
                    {
                        "detail": "Barber not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            if barber.pk!=pk:
                return Response( { "detail": "Access denied." }, status=status.HTTP_403_FORBIDDEN, )

            serializer = StaffProfileSerializer( barber )

            return Response( serializer.data, status=status.HTTP_200_OK, )

        # -----------------------------------------
        # List barbers
        # -----------------------------------------

        barbers = (
            StaffProfile.objects.select_related("user").filter(
                                    user__role=User.Role.STAFF,
                                    department=StaffProfile.Department.BARBER,
                                )
        )

        serializer = StaffProfileSerializer( barbers, many=True, )

        return Response( serializer.data, status=status.HTTP_200_OK, )

    def patch(self, request, pk=None):
        """
        Update the currently authenticated barber.

        Example:

            PATCH /api/barbers/me/

        This updates request.user, NOT a user identified
        by pk.
        """

        user = request.user

        # -----------------------------------------
        # Security check
        # -----------------------------------------

        if (
            user.role != User.Role.STAFF
            or not hasattr(user, "staffprofile")
            or user.staffprofile.department
            != StaffProfile.Department.BARBER
        ):
            return Response(
                {
                    "detail":
                        "Only authenticated barbers can "
                        "update their account."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # -----------------------------------------
        # Validate/update User
        # -----------------------------------------

        serializer = AllStaff_Self_UpdateSerializer(user, data=request.data, partial=True, )

        serializer.is_valid( raise_exception=True )

        serializer.save()

        # -----------------------------------------
        # Return updated barber
        # -----------------------------------------

        staff = (
            StaffProfile.objects
            .select_related("user")
            .get(pk=user.staffprofile.pk)
        )

        response_serializer = StaffProfileSerializer(
            staff
        )

        return Response( response_serializer.data, status=status.HTTP_200_OK, )

    def put(self, request, pk=None):
        """
        Full account update for the currently
        authenticated barber.

        PATCH is normally preferable for profile
        updates because it allows partial updates.
        """

        user = request.user

        if (
            user.role != User.Role.STAFF
            or not hasattr(user, "staffprofile")
            or user.staffprofile.department
            != StaffProfile.Department.BARBER
        ):
            return Response(
                {
                    "detail":
                        "Only authenticated barbers can "
                        "update their account."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AllStaff_Self_UpdateSerializer(user, data=request.data, partial=False, )

        serializer.is_valid( raise_exception=True )

        serializer.save()

        staff = ( StaffProfile.objects.select_related("user").get(pk=user.staffprofile.pk) )

        response_serializer = StaffProfileSerializer( staff )

        return Response( response_serializer.data, status=status.HTTP_200_OK, )


class AllStaffs_Api_View(APIView):
    #  this view give salon-manager group access to administrate over staffs
    permission_classes = [Is_SalonManager]

    def get(self, request, pk=None):

        if pk is not None:

            staff = StaffProfile.objects.filter(pk=pk, user__role=User.Role.STAFF).first()

            if staff is None:

                return Response({}, status=status.HTTP_404_NOT_FOUND)

            serializer = StaffProfileSerializer_2(staff)


            return Response(serializer.data,status=status.HTTP_200_OK )

        # is_active = request.query_params.get("staff_status") or None

        staff_status = request.query_params.get("staff_status") or None

        name_or_username = request.query_params.get("staff_name") or None

        department = request.query_params.get("staff_department") or None

        phone = request.query_params.get("staff_phone_number") or None

        all_staffs = StaffProfile.objects.all()
        # all_staffs = StaffProfile.objects.filter(user__is=True)

        # status
        if staff_status is not None:

            staff_status = staff_status.strip().lower()
            checked_staff_status = StaffProfile.StaffStatus.is_obj_of_staff_status(
                staff_status.strip())

            all_staffs = all_staffs.filter(status=checked_staff_status.value)

        # name
        if name_or_username is not None:

            all_staffs = all_staffs.filter(
                Q(user__last_name__icontains=name_or_username.strip()) |
                Q(user__first_name__icontains=name_or_username.strip()) |
                Q(user__username__icontains=name_or_username.strip())
            ).distinct()

        # phone
        if phone is not None:

            all_staffs = all_staffs.filter( user__phone_number__icontains=phone)

        # department
        if department is not None:

            all_staffs = all_staffs.filter(department__icontains=department)

        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(all_staffs, request)

        serializer = StaffProfileSerializer_2(page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

            serializer = StaffWriteSerializer( data=request.data )

            serializer.is_valid( raise_exception=True )

            staff = serializer.save()

            return Response(
                StaffProfileSerializer_2(staff).data,
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, pk):

        staff = (StaffProfile.objects.select_related("user").filter(
                                                            pk=pk,
                                                            user__role=User.Role.STAFF,
            ) .first()
        )

        if staff is None:
            return Response( {}, status=status.HTTP_404_NOT_FOUND, )

        serializer = StaffWriteSerializer( staff, data=request.data, )

        serializer.is_valid( raise_exception=True )

        staff = serializer.save()

        return Response( StaffProfileSerializer_2(staff).data, status=status.HTTP_200_OK, )

    def patch(self, request, pk):

        staff = (
            StaffProfile.objects.select_related("user")
            .filter( pk=pk, user__role=User.Role.STAFF, ).first()
        )

        if staff is None:
            return Response( {}, status=status.HTTP_404_NOT_FOUND, )

        serializer = StaffWriteSerializer( staff, data=request.data, partial=True, )

        serializer.is_valid( raise_exception=True )

        staff = serializer.save()

        return Response( StaffProfileSerializer_2(staff).data, status=status.HTTP_200_OK, )

    def delete(self, request, pk):

        staff = (
            StaffProfile.objects.select_related("user")
            .filter(
                pk=pk,
                user__role=User.Role.STAFF,
            )
            .first()
        )

        if staff is None:
            return Response(
                {
                    "detail": "Staff not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        delete_staff( staff=staff, )

        return Response( status=status.HTTP_204_NO_CONTENT )


class StaffUserDetails_Api_View(APIView):

    # this method should only allow the authenticated user get it own details

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated


    def get(self, request):

        if request.user.role != User.Role.STAFF:
            return Response(
                {"detail": "You are not authorized to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffProfileUserDetailsSerializer(request.user.staffprofile )

        return Response(serializer.data.get("user"), status=status.HTTP_200_OK)


class StaffsWorkingToday_Api_View(APIView):
    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        today_date = timezone.localdate()

        blocked_today = BreakTimeAndOffDays.objects.filter(
            staff=OuterRef("pk"),
            date=today_date,
        ).exclude(
            status=BreakTimeAndOffDays.BlockStatus.BREAK
        )

        staffs_working_today = StaffProfile.objects.filter(
            user__is_active=True
        ).annotate(
            is_blocked_today=Exists(blocked_today)
        ).filter(
            is_blocked_today=False
        )

        serializer = StaffsWorkingTodaySerializer(staffs_working_today, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get("refreshToken")

        if not refresh_token:

            return Response(
                {"detail": "Refresh token not found."},
                status=401
            )

        serializer = self.get_serializer(
            data={"refresh": refresh_token}
        )

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)


class StaffDepartmentAndPositionAndStatus_Api_View(APIView):
    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        staff_statuses_temp = StaffProfile.StaffStatus.choices
        staff_statuses = []
        for status1 in staff_statuses_temp:
            staff_statuses.append({"value": status1[0], "label": status1[1]})

        staff_positions_temp = StaffProfile.Position.choices
        staff_positions = []
        for position in staff_positions_temp:
            staff_positions.append({"value": position[0], "label": position[1]})

        staff_departments_temp = StaffProfile.Department.choices
        staff_departments = []
        for department in staff_departments_temp:
            staff_departments.append({"value": department[0], "label": department[1]})

        data = {"staff_statuses": staff_statuses, "staff_departments": staff_departments,
                "staff_positions": staff_positions}

        return Response(data, status=status.HTTP_200_OK)


class AllStaff_Self_Account_Update_Api_View(APIView):

    permission_classes = [ Is_Authenticated_Staff_User, ]

    parser_classes = [ MultiPartParser, FormParser, JSONParser, ]


    def patch(self, request):

        user = request.user

        if (user.role != User.Role.STAFF or not hasattr(user, "staffprofile") ):
            return Response(
                { "detail": "Only authenticated barbers can update this account." },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AllStaff_Self_UpdateSerializer(user, data=request.data, partial=True, )

        serializer.is_valid(  raise_exception=True )

        serializer.save()

        staff = ( StaffProfile.objects.select_related("user").get(user=user) )

        response_serializer = StaffProfileSerializer( staff )

        return Response( response_serializer.data, status=status.HTTP_200_OK, )

    def put(self, request):

        user = request.user

        if (
            user.role != User.Role.STAFF
            or not hasattr(user, "staffprofile")
        ):
            return Response(
                { "detail": "Only authenticated barbers can update this account." },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AllStaff_Self_UpdateSerializer(user, data=request.data, partial=False, )

        serializer.is_valid( raise_exception=True )

        serializer.save()

        staff = ( StaffProfile.objects.select_related("user").get(user=user) )

        response_serializer = StaffProfileSerializer( staff )

        return Response( response_serializer.data,  status=status.HTTP_200_OK,  )
