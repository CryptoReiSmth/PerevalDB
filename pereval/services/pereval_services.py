from django.db import transaction
from django.utils.dateparse import parse_datetime

from ..models import User, Coords, ActivityType, Pereval, PerevalLevel, PerevalImage


class PerevalService:
    @staticmethod
    def create_user(user_data: dict) -> User:
        """
        Создает пользователя или возвращает существующего по email и обновляет поля.
        """
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'phone': user_data.get('phone', ''),
                'fam': user_data.get('fam', ''),
                'name': user_data.get('name', ''),
                'otc': user_data.get('otc', ''),
            }
        )

        if not created:
            updated = False

            if user.phone != user_data.get('phone', user.phone):
                user.phone = user_data.get('phone', user.phone)
                updated = True
            if user.fam != user_data.get('fam', user.fam):
                user.fam = user_data.get('fam', user.fam)
                updated = True
            if user.name != user_data.get('name', user.name):
                user.name = user_data.get('name', user.name)
                updated = True
            if user.otc != user_data.get('otc', user.otc):
                user.otc = user_data.get('otc', user.otc)
                updated = True

            if updated:
                user.save()

        return user

    @staticmethod
    def create_coords(coords_data: dict) -> Coords:
        """
        Создает запись с координатами.
        """
        return Coords.objects.create(
            latitude=coords_data['latitude'],
            longitude=coords_data['longitude'],
            height=coords_data['height'],
        )

    @staticmethod
    def create_level(pereval: Pereval, level_data: dict) -> PerevalLevel:
        """
        Создает уровни для перевала.
        """
        return PerevalLevel.objects.create(
            pereval=pereval,
            winter=level_data.get('winter', ''),
            spring=level_data.get('spring', ''),
            summer=level_data.get('summer', ''),
            autumn=level_data.get('autumn', ''),
        )

    @staticmethod
    def create_images(pereval: Pereval, images_data: list) -> list:
        """
        Создает записи фотографий.
        """
        created_images = []

        for image_item in images_data:
            image_obj = PerevalImage.objects.create(
                pereval=pereval,
                title=image_item.get('title', ''),
                image=image_item['image'],
            )
            created_images.append(image_obj)

        return created_images

    @staticmethod
    def get_activity_type(activity_title: str | None) -> ActivityType | None:
        """
        Возвращает тип активности по названию.
        """
        if not activity_title:
            return None

        activity_type, _ = ActivityType.objects.get_or_create(title=activity_title)
        return activity_type

    @staticmethod
    @transaction.atomic
    def create_pereval(data: dict) -> Pereval:
        """
        Создание перевала со всеми связанными сущностями.
        """
        user = PerevalService.create_user(data['user'])
        coords = PerevalService.create_coords(data['coords'])
        activity_type = PerevalService.get_activity_type(data.get('activity_type'))

        add_time_raw = data.get('add_time')
        add_time = parse_datetime(add_time_raw) if add_time_raw else None

        pereval = Pereval.objects.create(
            beauty_title=data.get('beauty_title', ''),
            title=data['title'],
            other_titles=data.get('other_titles', ''),
            connect=data.get('connect', ''),
            region=data.get('region', ''),
            add_time=add_time,
            user=user,
            coords=coords,
            activity_type=activity_type,
            status='new',
        )

        PerevalService.create_level(pereval, data.get('level', {}))
        PerevalService.create_images(pereval, data.get('images', []))

        return pereval
