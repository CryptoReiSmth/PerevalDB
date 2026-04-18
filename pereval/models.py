from django.db import models


class User(models.Model):
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20)
    fam = models.CharField('Фамилия', max_length=100)
    name = models.CharField('Имя', max_length=100)
    otc = models.CharField('Отчество', max_length=100, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.fam} {self.name}'


class Coords(models.Model):
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6)
    height = models.PositiveIntegerField('Высота')

    class Meta:
        db_table = 'coords'
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return f'{self.latitude}, {self.longitude}, {self.height} м'


class ActivityType(models.Model):
    title = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        db_table = 'spr_activities_types'
        verbose_name = 'Тип активности'

    def __str__(self):
        return self.title


class Pereval(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('pending', 'На модерации'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонён'),
    )

    short_title = models.CharField('Сокращённое название', max_length=50, blank=True)
    title = models.CharField('Название перевала', max_length=255)
    other_titles = models.CharField('Другие названия', max_length=255, blank=True)
    connect = models.TextField('Что соединяет', blank=True)

    # вместо pereval_areas
    region = models.CharField('Район', max_length=255, blank=True)

    add_time = models.DateTimeField('Время добавления')
    date_added = models.DateTimeField('Дата записи', auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='perevals',
        verbose_name='Пользователь'
    )
    coords = models.OneToOneField(
        Coords,
        on_delete=models.CASCADE,
        related_name='pereval',
        verbose_name='Координаты'
    )

    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perevals',
        verbose_name='Тип активности'
    )

    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='new'
    )

    class Meta:
        db_table = 'pereval_added'
        verbose_name = 'Перевал'
        verbose_name_plural = 'Перевалы'

    def __str__(self):
        return self.title


class PerevalLevel(models.Model):
    pereval = models.OneToOneField(
        Pereval,
        on_delete=models.CASCADE,
        related_name='level',
        verbose_name='Перевал'
    )
    winter = models.CharField('Зима', max_length=10, blank=True)
    spring = models.CharField('Весна', max_length=10, blank=True)
    summer = models.CharField('Лето', max_length=10, blank=True)
    autumn = models.CharField('Осень', max_length=10, blank=True)

    class Meta:
        db_table = 'pereval_levels'
        verbose_name = 'Категория сложности'

    def __str__(self):
        return f'Категории для {self.pereval.title}'


class PerevalImage(models.Model):
    pereval = models.ForeignKey(
        Pereval,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Перевал'
    )
    title = models.CharField('Название фото', max_length=255, blank=True)
    image = models.ImageField('Фотография', upload_to='pereval_images/%Y/%m/%d/')
    date_added = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        db_table = 'pereval_images'
        verbose_name = 'Фотография перевала'

    def __str__(self):
        return f"{self.title} - {self.image}"
