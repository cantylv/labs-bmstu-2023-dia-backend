# from django.contrib import admin
# from django.db import models
# from django.urls import reverse


# class BidAdmin(models.Model):
#     list_display = ('users', 'moderator', 'date_create', 'date_formation', 'date_finish', 'status')


# class Bid(models.Model):
#     user = models.ForeignKey('Users', models.DO_NOTHING, verbose_name='ID пользователя')
#     moderator = models.ForeignKey('Users', models.DO_NOTHING, related_name='bid_moderator_set',
#                                   blank=True, null=True, verbose_name='ID модератора')
#     date_create = models.DateField(blank=True, null=True, verbose_name='Время создания')
#     date_formation = models.DateField(blank=True, null=True, verbose_name='Время формирования')
#     date_finish = models.DateField(blank=True, null=True, verbose_name='Время завершения')
#     status = models.ForeignKey('BidStatus', models.DO_NOTHING, blank=True, null=True, verbose_name='Статус')

#     class Meta:
#         managed = False
#         db_table = 'bid'
#         verbose_name = 'Заявка'
#         verbose_name_plural = 'Заявки'
#         ordering = ['date_create']

#     def __str__(self):
#         return self.pk


# class BidRecordAdmin(admin.ModelAdmin):
#     list_display = ('service', 'bid')


# class BidRecord(models.Model):
#     service = models.ForeignKey('Services', models.DO_NOTHING, verbose_name='ID услуги')
#     bid = models.ForeignKey(Bid, models.DO_NOTHING, verbose_name='ID заявки')

#     class Meta:
#         managed = False
#         db_table = 'bidrecord'
#         verbose_name = 'Заявка (вспомогательная табл.)'
#         verbose_name_plural = 'Заявки пользователей (вспомогательная табл.)'


# class BidStatus(models.Model):
#     status = models.CharField(max_length=20, blank=True, null=True, verbose_name='Название')

#     class Meta:
#         managed = False
#         db_table = 'bidstatus'
#         verbose_name = 'Статус заявки'
#         verbose_name_plural = 'Статусы заявок'


# class ServicesAdmin(admin.ModelAdmin):
#     list_display = ('id', 'job', 'about', 'age', 'rus_passport', 'insurance', 'status')
#     list_display_links = ('id', 'job')
#     search_fields = ('job', 'about')
#     list_editable = ('status', 'rus_passport', 'insurance')
#     list_filter = ('status', )


# class Services(models.Model):
#     job = models.CharField(max_length=50, verbose_name='Название профессии')
#     img = models.ImageField(upload_to="users/", verbose_name='Фотография')
#     about = models.TextField(blank=True, null=True, verbose_name='О работе')
#     age = models.IntegerField(verbose_name='Возраст')
#     rus_passport = models.BooleanField(blank=True, null=True, verbose_name='Наличие Российского Гражданства')
#     insurance = models.BooleanField(blank=True, null=True, verbose_name='Наличие мед. страховки')
#     status = models.CharField(max_length=15, blank=True, null=True, verbose_name='Статус')

#     class Meta:
#         managed = False
#         db_table = 'services'
#         verbose_name = 'Услуга'
#         verbose_name_plural = 'Услуги'

#     def __str__(self):
#         return self.job

#     def get_absolute_url(self):
#         return reverse('service', kwargs={'service_id': self.pk})


# class UsersAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'surname', 'isAdmin')
#     search_fields = ('name', 'surname')
#     list_editable = ('isAdmin', )
#     list_filter = ('isAdmin', )


# class Users(models.Model):
#     name = models.CharField(max_length=20, verbose_name='Имя')
#     surname = models.CharField(max_length=20, verbose_name='Фамилия')
#     isAdmin = models.BooleanField(default=False, blank=True, null=True, verbose_name='Является модератором')

#     class Meta:
#         managed = False
#         db_table = 'users'
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'

#     def __str__(self):
#         return self.name
