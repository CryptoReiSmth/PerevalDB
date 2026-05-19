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

    @staticmethod
    @transaction.atomic
    def update_pereval(pereval, data: dict):
        if pereval.status != 'new':
            return {
                'state': 0,
                'message': 'Редактировать можно только записи со статусом new'
            }

        if 'user' in data:
            old_user = pereval.user
            new_user = data['user']

            if (
                    old_user.email != new_user.get('email') or
                    old_user.fam != new_user.get('fam') or
                    old_user.name != new_user.get('name') or
                    old_user.otc != new_user.get('otc', '') or
                    old_user.phone != new_user.get('phone')
            ):
                return {
                    'state': 0,
                    'message': 'Нельзя изменять ФИО, email и телефон пользователя'
                }

        pereval.beauty_title = data.get('beauty_title', pereval.beauty_title)
        pereval.title = data.get('title', pereval.title)
        pereval.other_titles = data.get('other_titles', pereval.other_titles)
        pereval.connect = data.get('connect', pereval.connect)
        pereval.add_time = data.get('add_time', pereval.add_time)

        coords_data = data.get('coords')
        if coords_data:
            pereval.coords.latitude = coords_data.get(
                'latitude',
                pereval.coords.latitude
            )
            pereval.coords.longitude = coords_data.get(
                'longitude',
                pereval.coords.longitude
            )
            pereval.coords.height = coords_data.get(
                'height',
                pereval.coords.height
            )
            pereval.coords.save()

        level_data = data.get('level')
        if level_data:
            pereval.level.winter = level_data.get(
                'winter',
                pereval.level.winter
            )
            pereval.level.spring = level_data.get(
                'spring',
                pereval.level.spring
            )
            pereval.level.summer = level_data.get(
                'summer',
                pereval.level.summer
            )
            pereval.level.autumn = level_data.get(
                'autumn',
                pereval.level.autumn
            )
            pereval.level.save()

        images_data = data.get('images')
        if images_data:
            pereval.images.all().delete()

            for image_item in images_data:
                PerevalImage.objects.create(
                    pereval=pereval,
                    title=image_item.get('title', ''),
                    image=image_item['data'],
                )

        pereval.save()

        return {
            'state': 1,
            'message': None
        }
