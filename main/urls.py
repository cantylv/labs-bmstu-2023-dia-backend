from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # страница с услугами
    path('services/<int:service_id>/', views.service, name='service'),  # страница услуги
    path('user/draft/', views.draft, name='draft') # cтраница черновика
]