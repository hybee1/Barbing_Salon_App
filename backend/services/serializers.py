
from rest_framework import serializers

from backend.services.models import Service, Hairstyle, Color


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ["id", "name", "image", "price", "duration_minutes" ,
                  "description", "is_active"]


class HairstyleSerializer(serializers.ModelSerializer):

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    class Meta:
        model = Hairstyle
        fields = [
            "id", "service", "name", "image", "price", "duration_minutes",
            "description", "is_active",
        ]


class HairstyleReadSerializer(serializers.ModelSerializer):

    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Hairstyle
        fields = [
            "id", "service", "name", "image", "price",
            "duration_minutes", "description", "is_active",
        ]


class HairstylesWithoutServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hairstyle
        fields = [ "id", "name", "image" , "price",
                   "description", "is_active"]


class ServiceAndItHairstylesSerializer(serializers.ModelSerializer):

    hairstyles = HairstylesWithoutServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id", "name", "image", "price", "duration_minutes",
            "description", "is_active", "hairstyles",
        ]


class ServicesWithHairstylesButOnlyServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [ "id", "name", ]


class ColorSerializer(serializers.ModelSerializer):

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    class Meta:
        model = Color
        fields = [
            "id", "service", "name", "price",
            "description", "duration_minutes", "is_active",
        ]


class ColorReadSerializer(serializers.ModelSerializer):

    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Color
        fields = [
            "id", "service", "name", "price", "description",
            "duration_minutes", "is_active",
        ]

class ColorsWithoutServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = [ "id", "name", "description" , "price",
                   "duration_minutes", "is_active"]

class ServiceAndItColorsSerializer(serializers.ModelSerializer):

    colors = ColorsWithoutServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id", "name", "image", "price", "duration_minutes",
            "description", "is_active", "colors",
        ]


class ServicesWithColorsButOnlyServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [ "id", "name", ]


class Service_With_It_Hairstyles_And_Colors_Serializer(serializers.ModelSerializer):

    hairstyles = HairstylesWithoutServiceSerializer(many=True, read_only=True)
    colors = ColorsWithoutServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id", "name", "image", "price", "duration_minutes",
            "description", "is_active", "hairstyles", "colors",
        ]