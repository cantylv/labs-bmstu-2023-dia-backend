from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *

api_version = r'api/v1'
router = routers.DefaultRouter()
router.register(rf'{api_version}/user', UserViewSet, basename='user')


schema_view = get_schema_view(
   openapi.Info(
      title="REST API DRF",
      default_version='v1',
      description= "Описание API веб-сервиса, который будет отдавать данные из БД и менять их.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True
)

urlpatterns = [
   path(f'', include(router.urls)),

   ### Домен услуг ###
   path(rf'{api_version}/services/', ServiceList.as_view(), name='ServicesList'),  # список услуг или добавление новой услуги
   path(rf'{api_version}/services/<int:service_id>/', ServiceDetail.as_view(), name='ServicesDetail'),  # получение/изменение/удаление услуги
   path(rf'{api_version}/services/<int:service_id>/img/', PictureImage.as_view(), name='ServicesImage'),  # получение/изменение фотографии
   path(rf'{api_version}/services/add/<int:service_id>/', AddServiceToDraft, name='AddServicesToDraft'),  # добавление услуги в черновик

   ### Домен заявок ###
   path(rf'{api_version}/bids/', BidList.as_view(), name='Bidslist'), # получение списка заявок
   path(rf'{api_version}/bids/<int:bid_id>/', BidDetail.as_view(), name='BidsDetail'),  # получение данных о заявке
   path(rf'{api_version}/bids/<int:bid_id>/new_status/', ChangeBidStatus, name='ChangeBidsStatus'),  # отклонение/принятие заявки

   ### Домен пользователя ###
   path(rf'{api_version}/login/',  UserLogin, name='Login'),  # авторизация пользователя
   path(rf'{api_version}/logout/', UserLogout, name='Logout'),  # выход из системы = удаление cookie авторизации

   ### Домен м-м ###
   path(rf'{api_version}/delete_service/<int:service_id>/bids/<int:bid_id>/', DeleteServiceFromDraft, name='DeleteServicesFromDraft'),  # удаление услуги из черновика

   ### Документация ###
   path('swagger/', schema_view.with_ui(), name='schema-swagger-ui')  # документация API v1
]