from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
import django.utils.timezone as timezone


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, verbose_name="Никнейм")
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Имя')
    second_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Фамилия')
    email = models.EmailField(max_length=150, blank=True, null=True, verbose_name="Электронная почта")
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Номер телефона")
    password = models.CharField(max_length=150, verbose_name='Пароль')
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    is_staff = models.BooleanField(default=False, verbose_name="Есть ли у пользователя привелегии?")
    is_active = models.BooleanField(default=True, verbose_name="Является ли пользователь активным?")
    last_login = models.DateTimeField(default=timezone.now, verbose_name="Время последнего посещения")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Время регистрации в системе')

    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        managed = True
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Service(models.Model):
    MALE = "M"
    FEMALE = "F"
    ANYONE = "A"
    SEX = [
        (MALE, "Мужской"),
        (FEMALE, "Женский"),
        (ANYONE, "Любой")
    ]
    job = models.CharField(max_length=150, verbose_name='Название профессии')
    img = models.CharField(max_length=150, default='default.jpg', verbose_name='Адрес фото в minio')
    about = models.TextField(blank=True, verbose_name='Описание работы')
    age = models.IntegerField(default=14,
                              verbose_name='Возраст')  # с 14 лет можно стать самозанятым с согласия родителей
    sex = models.CharField(max_length=1, choices=SEX, default=ANYONE, verbose_name="Пол")
    rus_passport = models.BooleanField(default=False, verbose_name='Наличие Гражданства РФ')
    insurance = models.BooleanField(default=False, verbose_name='Наличие медицинской страховки')
    status = models.BooleanField(default=True, verbose_name='Активна?')  # False - удалена, True - действует
    salary = models.IntegerField(verbose_name="Оплата труда")
    date_start = models.DateTimeField(verbose_name="Начало работы", db_comment="Начальное время работы")
    date_end = models.DateTimeField(verbose_name="Конец работы", db_comment="Конечное время работы")

    class Meta:
        managed = True
        db_table = 'Service'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.job


class Bid(models.Model):
    DRAFT = "draft"
    DELETED = "deleted"
    FORMED = "formed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    BID_STATUS = [
        (DRAFT, "Черновик"),
        (DELETED, "Удалено"),
        (FORMED, "Сформировано"),
        (COMPLETED, "Завершено"),
        (REJECTED, "Отклонено")
    ]
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='user_bids',
                             verbose_name='Идентификатор пользователя')
    moderator = models.ForeignKey('CustomUser', on_delete=models.CASCADE, blank=True, null=True,
                                  related_name='moderator_bids', verbose_name='Идентификатор модератора')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')  # время добавления в корзину
    date_formation = models.DateTimeField(blank=True, null=True,
                                          verbose_name='Время формирования')  # время отправки модератору на рассмотрение
    date_finish = models.DateTimeField(blank=True, null=True,
                                       verbose_name='Время завершения')  # время рассмотрения модератором заявки
    status = models.CharField(max_length=10, choices=BID_STATUS, default=DRAFT, verbose_name='Статус')
    services = models.ManyToManyField('Service', db_table='ServiceBid', blank=True, verbose_name="Услуги")

    class Meta:
        managed = True
        db_table = 'Bid'
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['date_create']

    def __str__(self):
        return self.user.username


# Для админки
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'moderator', 'date_create', 'date_formation', 'date_finish', 'status')
    list_filter = ('date_create', 'date_formation', 'date_finish', 'status')


class ServiceAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'job', 'img', 'about', 'age', 'sex', 'rus_passport', 'insurance', 'salary', 'status', 'date_start',
    'date_end')
    list_display_links = ('job',)
    search_fields = ('job', 'about')
    list_editable = ('status', 'rus_passport', 'insurance', 'salary')
    list_filter = ('status', 'rus_passport', 'date_start', 'date_end')


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'second_name', 'email', 'phone',
                    'is_superuser', 'is_active', 'last_login', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    list_editable = ('is_superuser', 'is_active', 'first_name', 'second_name', 'email', 'phone')