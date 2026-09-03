
from django.db.models import Q, OuterRef, Exists
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework.response import Response
from rest_framework.views import APIView

from backend.accounts.models import User, StaffProfile
from backend.accounts.serializers import StaffProfileSerializer, StaffProfileUserDetailsSerializer, \
    StaffsWorkingTodaySerializer, StaffProfileSerializer_2,  StaffWriteSerializer, \
    BarberSelfUpdateSerializer
from backend.accounts.services import delete_staff
from backend.breakperiods.models import BreakTimeAndOffDays

from rest_framework_simplejwt.views import TokenRefreshView

from backend.custom_permissions.permissions import Is_Authenticated_Staff_User
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
    # this class is method is for update of staffs not only barber
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

        serializer = BarberSelfUpdateSerializer( user, data=request.data, partial=True, )

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

        serializer = BarberSelfUpdateSerializer( user, data=request.data, partial=False, )

        serializer.is_valid( raise_exception=True )

        serializer.save()

        staff = ( StaffProfile.objects.select_related("user").get(pk=user.staffprofile.pk) )

        response_serializer = StaffProfileSerializer( staff )

        return Response( response_serializer.data, status=status.HTTP_200_OK, )


class AllStaffs_Api_View(APIView):
    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request, pk=None):

        if pk is not None:
            print("AllStaffsView when pk 1")
            staff = StaffProfile.objects.filter(pk=pk, user__role=User.Role.STAFF).first()

            print("AllStaffsView when pk 2")

            if staff is None:
                print("AllStaffsView when pk 2a")
                return Response({}, status=status.HTTP_404_NOT_FOUND)

            print("AllStaffsView when pk 3")
            serializer = StaffProfileSerializer_2(staff)

            print("AllStaffsView when pk 4")
            print("serializer.data = ", serializer.data)
            return Response(serializer.data,status=status.HTTP_200_OK )

        print("AllStaffsView 1")

        # is_active = request.query_params.get("staff_status") or None
        # print("is_active", is_active)

        staff_status = request.query_params.get("staff_status") or None
        print("staff_status", staff_status)

        name_or_username = request.query_params.get("staff_name") or None
        print("name_or_username", name_or_username)

        department = request.query_params.get("staff_department") or None
        print("department", department)

        phone = request.query_params.get("staff_phone_number") or None
        print("phone", phone)

        print("AllStaffsView 2")

        all_staffs = StaffProfile.objects.all()
        # all_staffs = StaffProfile.objects.filter(user__is=True)

        print("AllStaffsView 3")

        # status
        if staff_status is not None:
            print("AllStaffsView 3a")
            staff_status = staff_status.strip().lower()
            checked_staff_status = StaffProfile.StaffStatus.is_obj_of_staff_status(
                staff_status.strip())

            all_staffs = all_staffs.filter(status=checked_staff_status.value)

        print("AllStaffsView 4")
        # name
        if name_or_username is not None:
            print("ALlStaffsView 4a")
            all_staffs = all_staffs.filter(
                Q(user__last_name__icontains=name_or_username.strip()) |
                Q(user__first_name__icontains=name_or_username.strip()) |
                Q(user__username__icontains=name_or_username.strip())
            ).distinct()

        print("AllStaffsView 5")

        # phone
        if phone is not None:
            print("ALlStaffsView 5a")
            all_staffs = all_staffs.filter( user__phone_number__icontains=phone)

        print("AllStaffsView 6")

        # department
        if department is not None:
            print("ALlStaffsView 6a")
            all_staffs = all_staffs.filter(department__icontains=department)

        print("AllStaffsView 7")
        paginator = StandardResultsSetPagination()
        print("ALlStaffsView 8")
        page = paginator.paginate_queryset(all_staffs, request)

        print("AllStaffsView 9")
        serializer = StaffProfileSerializer_2(page, many=True)

        print("AllStaffsView 10")

        print("serializer.data = ", serializer.data)

        print("AllStaffsView 11")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

            serializer = StaffWriteSerializer( data=request.data )

            print("post data = ", request.data)

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

    permission_classes = [Is_Authenticated_Staff_User]  # user must be authenticated


    def get(self, request):

        if request.user.role != User.Role.STAFF:
            return Response(
                {"detail": "You are not authorized to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffProfileUserDetailsSerializer(request.user.staffprofile )
        print("user serializer", serializer.data)
        return Response(serializer.data.get("user"), status=status.HTTP_200_OK)


class StaffsWorkingToday_Api_View(APIView):
    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        print("StaffsWorkingTodayAPIView 1")

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

        print("StaffsWorkingTodayAPIView 2")

        serializer = StaffsWorkingTodaySerializer(staffs_working_today, many=True)

        print("StaffsWorkingTodayAPIView 3")

        print("StaffsWorkingTodayAPIView = ", serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        print("CookieTokenRefreshView 1")
        refresh_token = request.COOKIES.get("refreshToken")

        print("CookieTokenRefreshView 2")
        if not refresh_token:
            print("CookieTokenRefreshView 2a")
            return Response(
                {"detail": "Refresh token not found."},
                status=401
            )

        print("CookieTokenRefreshView 3")
        serializer = self.get_serializer(
            data={"refresh": refresh_token}
        )

        print("CookieTokenRefreshView 4")
        serializer.is_valid(raise_exception=True)

        print("CookieTokenRefreshView 5")
        return Response(serializer.validated_data)


class StaffDepartmentAndPositionAndStatus_Api_View(APIView):
    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request):

        print("StaffDepartmentAndPositionAndStatusAPIView 1")

        staff_statuses_temp = StaffProfile.StaffStatus.choices
        staff_statuses = []
        for status1 in staff_statuses_temp:
            staff_statuses.append({"value": status1[0], "label": status1[1]})

        print("StaffDepartmentAndPositionAndStatusAPIView 2")

        staff_positions_temp = StaffProfile.Position.choices
        staff_positions = []
        for position in staff_positions_temp:
            staff_positions.append({"value": position[0], "label": position[1]})

        print("StaffDepartmentAndPositionAndStatusAPIView 3")

        staff_departments_temp = StaffProfile.Department.choices
        staff_departments = []
        for department in staff_departments_temp:
            staff_departments.append({"value": department[0], "label": department[1]})
        print("StaffDepartmentAndPositionAndStatusAPIView 4")

        data = {"staff_statuses": staff_statuses, "staff_departments": staff_departments,
                "staff_positions": staff_positions}

        print("data = ", data)

        print("StaffDepartmentAndPositionAndStatusAPIView 5")

        return Response(data, status=status.HTTP_200_OK)


class AllStaff_Self_Account_Update_Api_View(APIView):

    permission_classes = [ Is_Authenticated_Staff_User, ]

    parser_classes = [ MultiPartParser, FormParser, JSONParser, ]

    # def get(self, request):
    #
    #     user = request.user
    #
    #     if (
    #         user.role != User.Role.STAFF
    #         or not hasattr(user, "staffprofile")
    #         or user.staffprofile.department
    #         != StaffProfile.Department.BARBER
    #     ):
    #         return Response(
    #             { "detail": "Only authenticated barbers can access this endpoint." },
    #             status=status.HTTP_403_FORBIDDEN,
    #         )
    #
    #     staff = ( StaffProfile.objects .select_related("user") .get(user=user) )
    #
    #     serializer = StaffProfileSerializer( staff )
    #
    #     return Response( serializer.data, status=status.HTTP_200_OK, )

    def patch(self, request):

        user = request.user

        # if ( user.role != User.Role.STAFF or not hasattr(user, "staffprofile") or
        #         user.staffprofile.department != StaffProfile.Department.BARBER ):

        if (user.role != User.Role.STAFF or not hasattr(user, "staffprofile") ):
            return Response(
                { "detail": "Only authenticated barbers can update this account." },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BarberSelfUpdateSerializer( user, data=request.data, partial=True, )

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
            or user.staffprofile.department
            != StaffProfile.Department.BARBER
        ):
            return Response(
                { "detail": "Only authenticated barbers can update this account." },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BarberSelfUpdateSerializer( user, data=request.data, partial=False, )

        serializer.is_valid( raise_exception=True )

        serializer.save()

        staff = ( StaffProfile.objects.select_related("user").get(user=user) )

        response_serializer = StaffProfileSerializer( staff )

        return Response( response_serializer.data,  status=status.HTTP_200_OK,  )
