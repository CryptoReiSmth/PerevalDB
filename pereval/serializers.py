import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Pereval, PerevalImage


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fam = serializers.CharField()
    name = serializers.CharField()
    otc = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField()


class CoordsSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    height = serializers.IntegerField()


class LevelSerializer(serializers.Serializer):
    winter = serializers.CharField(required=False, allow_blank=True)
    summer = serializers.CharField(required=False, allow_blank=True)
    autumn = serializers.CharField(required=False, allow_blank=True)
    spring = serializers.CharField(required=False, allow_blank=True)


class ImageSerializer(serializers.Serializer):
    data = serializers.CharField()
    title = serializers.CharField(required=False, allow_blank=True)

    def validate_data(self, value):
        try:
            if ';base64,' in value:
                value = value.split(';base64,')[1]

            decoded_file = base64.b64decode(value)
            file_name = f'{uuid.uuid4()}.jpg'

            return ContentFile(decoded_file, name=file_name)
        except Exception:
            raise serializers.ValidationError('Некорректный формат изображения')


class PerevalSubmitSerializer(serializers.Serializer):
    beauty_title = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    other_titles = serializers.CharField(required=False, allow_blank=True)
    connect = serializers.CharField(required=False, allow_blank=True)
    add_time = serializers.DateTimeField()

    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer(required=False)
    images = ImageSerializer(many=True, required=False)


class PerevalImageReadSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = PerevalImage
        fields = ('data', 'title')

    def get_data(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None


class PerevalReadSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = PerevalImageReadSerializer(many=True)

    class Meta:
        model = Pereval
        fields = (
            'id',
            'beauty_title',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coords',
            'level',
            'images',
            'status',
        )
