
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SalonInfo, SalonBookingSetting
from .serializers import (SalonInfoReadSerializer, SalonBookingSettingSerializer,
                          SalonInfoWriteSerializer)

from ..custom_permissions.permissions import Is_Authenticated_Staff_User


class SalonConfig_And_Info_View(APIView):

    permission_classes = (Is_Authenticated_Staff_User,)

    def get(self, request):
        salon_info = SalonInfo.objects.all().first()
        salon_booking_setting = SalonBookingSetting.objects.all().first()
        salon_info_serializer = SalonInfoReadSerializer(salon_info)
        salon_booking_setting_serializer = SalonBookingSettingSerializer(salon_booking_setting)


        data = {
            "salon_info": salon_info_serializer.data,
            "salon_booking_buffer": salon_booking_setting_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)


class SalonInfoWebView(APIView):

    def get(self, request):
        salon_info = SalonInfo.objects.all().first()

        salon_serializer = SalonInfoReadSerializer(salon_info)

        return Response(salon_serializer.data, status=status.HTTP_200_OK)


class SalonInfoModifyView(APIView):

    def post(self, request):
        serializer = SalonInfoWriteSerializer(data=request.data)

        if serializer.is_valid():
            salon = serializer.save()

            return Response( SalonInfoWriteSerializer(salon).data, status=status.HTTP_201_CREATED )

        return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST )


class SalonBookingSettingView(APIView):

    def get(self, request):

        settings = SalonBookingSetting.objects.all()
        serializer = SalonBookingSettingSerializer( settings, many=True )

        return Response( serializer.data, status=status.HTTP_200_OK )

    def post(self, request):
        serializer = SalonBookingSettingSerializer(
            data=request.data
        )

        if serializer.is_valid():
            booking_setting = serializer.save()

            return Response(
                SalonBookingSettingSerializer(booking_setting).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
