
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.custom_permissions.permissions import Is_Authenticated_Staff_User
from backend.pagination.pagination import StandardResultsSetPagination
from backend.services.models import Service, Hairstyle, Color

from backend.services.serializers import (
    ServiceSerializer, HairstyleSerializer,
    ColorSerializer, ServiceAndItHairstylesSerializer, ServiceAndItColorsSerializer,
    Service_With_It_Hairstyles_And_Colors_Serializer, HairstyleReadSerializer,
    ColorReadSerializer, ServicesWithColorsButOnlyServiceSerializer,
    ServicesWithHairstylesButOnlyServiceSerializer
)

from rest_framework.parsers import MultiPartParser, FormParser


# --------------------
# SERVICES
# --------------------

class ServicesView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk=None):

        if pk is not None:
            service = get_object_or_404(Service, pk=pk)
            serializer = ServiceSerializer(service)
            return Response(serializer.data)

        service_name = request.query_params.get("service_name") or None
        print("service_name", service_name)

        service_price = request.query_params.get("service_price") or None
        print("service_price", service_price)

        service_duration_minutes = request.query_params.get("service_duration_minutes") or None
        print("service_duration_minutes", service_duration_minutes)

        service_is_active = request.query_params.get("service_is_active") or None
        print("service_is_active", service_is_active)

        services = Service.objects.all()

        # service_name
        if service_name is not None:
            services = services.filter(name__icontains=service_name)

        # service_price
        if service_price is not None:
            print("service_price instance", type(service_price))

            if (not isinstance(service_price, str) and not isinstance(service_price, int) and
                    not isinstance(service_price, float) and
                    not isinstance(service_price, Decimal)):
                raise serializers.ValidationError()

            if isinstance(service_price, str):
                try:
                    service_price = Decimal(service_price)
                except ValueError:
                    raise serializers.ValidationError()

            services = services.filter(price=service_price)

        # service_duration_minutes
        if service_duration_minutes is not None:
            print("service_duration_minutes instance", type(service_duration_minutes))

            if (not isinstance(service_duration_minutes, str) and
                             not isinstance(service_duration_minutes, int)):
                raise serializers.ValidationError()

            if isinstance(service_duration_minutes, str):
                try:
                    service_duration_minutes = int(service_duration_minutes)
                except ValueError:
                    raise serializers.ValidationError()

            services = services.filter( duration_minutes=service_duration_minutes)

        # service_is_active
        if service_is_active is not None:

            print("service_is_active instance", type(service_is_active))

            if not isinstance(service_is_active, str) and not isinstance(service_is_active, bool):
                raise serializers.ValidationError()

            if isinstance(service_is_active, str):
                if service_is_active.lower() == "true":
                    is_active = True

                elif service_is_active.lower() == "false":
                    is_active = False

            if isinstance(service_is_active, bool) :
                is_active = service_is_active

            services = services.filter(is_active=is_active)

            print("is_active = ", is_active)
            services = services.filter( is_active=is_active)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(services, request)

        serializer = ServiceSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


    def post(self, request):

        serializer = ServiceSerializer(  data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_201_CREATED )

    def put(self, request, pk):

        service = get_object_or_404(Service, pk=pk)

        serializer = ServiceSerializer( service, data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def patch(self, request, pk):

        service = get_object_or_404(Service, pk=pk)

        serializer = ServiceSerializer( service, data=request.data, partial=True )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def delete(self, request):

        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {"detail": "No service IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Service.objects.filter( id__in=ids ).delete()

        print("Deleted", deleted_count, "services")

        return Response( status=status.HTTP_204_NO_CONTENT )


# --------------------
# HAIRSTYLES
# --------------------

class HairstylesView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk=None):

        if pk is not None:
            hairstyle = get_object_or_404(Hairstyle, pk=pk)
            serializer = HairstyleSerializer(hairstyle)
            return Response(serializer.data)

        hairstyle_name = request.query_params.get("hairstyle_name") or None
        print("hairstyle_name", hairstyle_name)

        service_id = request.query_params.get("service_id") or None
        print("service_id", service_id)

        hairstyle_price = request.query_params.get("hairstyle_price") or None
        print("hairstyle_price", hairstyle_price)

        hairstyle_duration_minutes = request.query_params.get("hairstyle_duration_minutes") or None
        print("hairstyle_duration_minutes", hairstyle_duration_minutes)

        hairstyle_is_active = request.query_params.get("hairstyle_is_active") or None
        print("service_is_active", hairstyle_is_active)

        hairstyles = Hairstyle.objects.all()

        # hairstyles_name
        if hairstyle_name is not None:
            hairstyles = hairstyles.filter(name__icontains=hairstyle_name)

        # service_name
        if service_id is not None:
            print("service_id instance", type(service_id))

            if (not isinstance(service_id, str) and not isinstance(service_id, int)):
                raise serializers.ValidationError()

            if isinstance(service_id, str):
                try:
                    service_id = int(service_id)
                except ValueError:
                    raise serializers.ValidationError()

            hairstyles = hairstyles.filter(service=service_id)

        # hairstyle_price
        if hairstyle_price is not None:
            print("service_price instance", type(hairstyle_price))

            if (not isinstance(hairstyle_price, str) and not isinstance(hairstyle_price, int) and
                    not isinstance(hairstyle_price, float) and
                    not isinstance(hairstyle_price, Decimal)):
                raise serializers.ValidationError()

            if isinstance(hairstyle_price, str):
                try:
                    hairstyle_price = Decimal(hairstyle_price)
                except ValueError:
                    raise serializers.ValidationError()

            hairstyles = hairstyles.filter(price=hairstyle_price)

        # hairstyle_duration_minutes
        if hairstyle_duration_minutes is not None:
            print("service_duration_minutes instance", type(hairstyle_duration_minutes))

            if (not isinstance(hairstyle_duration_minutes, str) and
                    not isinstance(hairstyle_duration_minutes, int)):
                raise serializers.ValidationError()

            if isinstance(hairstyle_duration_minutes, str):
                try:
                    service_duration_minutes = int(hairstyle_duration_minutes)
                except ValueError:
                    raise serializers.ValidationError()

            hairstyles = hairstyles.filter(duration_minutes=hairstyle_duration_minutes)

        # hairstyle_is_active
        if hairstyle_is_active is not None:

            print("service_is_active instance", type(hairstyle_is_active))

            if not isinstance(hairstyle_is_active, str) and not isinstance(hairstyle_is_active, bool):
                raise serializers.ValidationError()

            if isinstance(hairstyle_is_active, str):
                if hairstyle_is_active.lower() == "true":
                    is_active = True

                elif hairstyle_is_active.lower() == "false":
                    is_active = False

            if isinstance(hairstyle_is_active, bool):
                is_active = hairstyle_is_active

            print("is_active = ", is_active)
            hairstyles = hairstyles.filter(is_active=is_active)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(hairstyles, request)

        serializer = HairstyleReadSerializer(page, many=True)

        print("HairstyleView", serializer.data)

        return paginator.get_paginated_response(serializer.data)


    def post(self, request):

        serializer = HairstyleSerializer( data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_201_CREATED )


    def put(self, request, pk):

        hairstyle = get_object_or_404( Hairstyle,  pk=pk )

        serializer = HairstyleSerializer( hairstyle, data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def patch(self, request, pk):

        hairstyle = get_object_or_404( Hairstyle, pk=pk )

        serializer = HairstyleSerializer( hairstyle, data=request.data, partial=True )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def delete(self, request):

        ids = request.data.get("ids", [])

        if not ids:

            return Response(
                {"detail": "No hairstyle IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Hairstyle.objects.filter( id__in=ids  ).delete()

        print("Deleted", deleted_count, "hairstyles")

        return Response( status=status.HTTP_204_NO_CONTENT  )


# --------------------
# COLORS
# --------------------

class ColorsView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk=None):

        if pk is not None:
            color = get_object_or_404(Color, pk=pk)
            serializer = ColorSerializer(color)
            return Response(serializer.data)


        color_name = request.query_params.get("color_name") or None
        print("color_name", color_name)

        service_id = request.query_params.get("service_id") or None
        print("service_id", service_id)

        color_price = request.query_params.get("color_price") or None
        print("color_price", color_price)

        color_duration_minutes = request.query_params.get("color_duration_minutes") or None
        print("color_duration_minutes", color_duration_minutes)

        color_is_active = request.query_params.get("color_is_active") or None
        print("color_is_active", color_is_active)

        colors = Color.objects.all()

        # color_name
        if color_name is not None:
            colors = colors.filter(name__icontains=color_name)

        # service_id
        if service_id is not None:
            print("service_id instance", type(service_id))

            if (not isinstance(service_id, str) and not isinstance(service_id, int)):
                raise serializers.ValidationError()

            if isinstance(service_id, str):
                try:
                    service_id = int(service_id)
                except ValueError:
                    raise serializers.ValidationError()

            colors = colors.filter(service=service_id)

        # color_price
        if color_price is not None:
            print("color_price instance", type(color_price))

            if (not isinstance(color_price, str) and not isinstance(color_price, int) and
                    not isinstance(color_price, float) and
                    not isinstance(color_price, Decimal)):
                raise serializers.ValidationError()

            if isinstance(color_price, str):
                try:
                    hairstyle_price = Decimal(color_price)
                except ValueError:
                    raise serializers.ValidationError()

            colors = colors.filter(price=hairstyle_price)

        # hairstyle_duration_minutes
        if color_duration_minutes is not None:
            print("color_duration_minutes instance", type(color_duration_minutes))

            if (not isinstance(color_duration_minutes, str) and
                    not isinstance(color_duration_minutes, int)):
                raise serializers.ValidationError()

            if isinstance(color_duration_minutes, str):
                try:
                    service_duration_minutes = int(color_duration_minutes)
                except ValueError:
                    raise serializers.ValidationError()

            colors = colors.filter(duration_minutes=color_duration_minutes)

        # hairstyle_is_active
        if color_is_active is not None:

            print("service_is_active instance", type(color_is_active))

            if not isinstance(color_is_active, str) and not isinstance(color_is_active, bool):
                raise serializers.ValidationError()

            if isinstance(color_is_active, str):
                if color_is_active.lower() == "true":
                    is_active = True

                elif color_is_active.lower() == "false":
                    is_active = False

            if isinstance(color_is_active, bool):
                is_active = color_is_active

            print("is_active = ", is_active)
            colors = colors.filter(is_active=is_active)


        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(colors, request)

        serializer = ColorReadSerializer(page, many=True)

        print("ColorsView", serializer.data)

        return paginator.get_paginated_response(serializer.data)


    def post(self, request):

        serializer = ColorSerializer( data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_201_CREATED )


    def put(self, request, pk):

        color = get_object_or_404( Color, pk=pk )

        serializer = ColorSerializer( color, data=request.data )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def patch(self, request, pk):

        color = get_object_or_404( Color, pk=pk )

        serializer = ColorSerializer( color, data=request.data, partial=True )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response( serializer.data, status=status.HTTP_200_OK )

    def delete(self, request):

        ids = request.data.get("ids", [])

        if not ids:

            return Response(
                {"detail": "No color IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Color.objects.filter( id__in=ids ).delete()

        print("Deleted", deleted_count, "colors")

        return Response( status=status.HTTP_204_NO_CONTENT )


# --------------------
# SERVICE WITH HAIRSTYLE BUT RETURN ONLY THE SERVICES
# --------------------

class ServicesWithHairstylesButOnlyServiceView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request ):
        services = Service.objects.filter(hairstyles__isnull=False).distinct()
        serializer = ServicesWithHairstylesButOnlyServiceSerializer( services, many=True )
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------
# SERVICE WITH HAIRSTYLES
# --------------------

class ServiceAndItsHairstylesView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk):

        service = get_object_or_404(
                                    Service.objects.prefetch_related("hairstyles"),
                                    pk=pk,
                                )

        serializer = ServiceAndItHairstylesSerializer( service )

        return Response( serializer.data, status=status.HTTP_200_OK )


# --------------------
# SERVICE WITH COLORS BUT RETURN ONLY THE SERVICE
# --------------------

class ServicesWithColorsButOnlyServiceView(APIView):

    permission_classes = [Is_Authenticated_Staff_User]

    def get(self, request ):
        services = Service.objects.filter(colors__isnull=False).distinct()
        serializer = ServicesWithColorsButOnlyServiceSerializer( services, many=True )
        return Response(serializer.data, status=status.HTTP_200_OK)

# --------------------
# SERVICE WITH COLORS
# --------------------

class ServiceAndItsColorsView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk):

        service = get_object_or_404(
                                    Service.objects.prefetch_related("colors"),
                                    pk=pk,
                                )

        serializer = ServiceAndItColorsSerializer(service)

        return Response(serializer.data, status=status.HTTP_200_OK)


        # colors = service.color.all()
        #
        # return Response(
        #     {
        #         "service": ServiceSerializer(service).data,
        #         "colors": ColorSerializer( colors, many=True ).data,
        #     },
        #     status=status.HTTP_200_OK
        # )


# --------------------
# SERVICE WITH HAIRSTYLE AND COLORS
# --------------------
class Service_With_It_Hairstyles_And_Colors_Api_View(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                Is_Authenticated_Staff_User,
                # OtherPermission,
                # AnotherPermission,
            ]

        return [permission() for permission in permission_classes]

    def get(self, request, pk):

        service = get_object_or_404(
                        Service.objects.prefetch_related("hairstyles", "colors"), pk=pk )

        serializer = Service_With_It_Hairstyles_And_Colors_Serializer(service)

        return Response(serializer.data, status=status.HTTP_200_OK)