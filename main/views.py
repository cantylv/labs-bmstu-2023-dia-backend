from django.views.decorators.http import require_GET
from django.shortcuts import render
from Engine.settings import BASE_DIR
from pathlib import Path
import os


from .models import *

# Локальная база данных
import random

# УСЛУГИ
JOBS = [
    {
        'name': 'Программирование',
        'uploads': 'img/professions/prog.jpg'
    },
    {
        'name': 'Массаж',
        'uploads': 'img/professions/massage.jpg'
    },
    {
        'name': 'Сантехнические работы',
        'uploads': 'img/professions/santechnik.jpg'
    },
    {
        'name': 'Автомойка',
        'uploads': 'img/professions/wash_car.jpg'
    },
    {
        'name': 'Ветеринария',
        'uploads': 'img/professions/veterinar.jpg'
    },
    {
        'name': 'Медицина',
        'uploads': 'img/professions/urolog.jpg'
    },
    {
        'name': 'Репетиторство',
        'uploads': 'img/professions/teacher.jpg'
    },
    {
        'name': 'Юриспруденция',
        'uploads': 'img/professions/jurist.jpg'
    },
    {
        'name': 'Охрана и безопасность',
        'uploads': 'img/professions/security.jpg'
    },
    {
        'name': 'Аналитика данных',
        'uploads': 'img/professions/datanal.jpg'
    },
    {
        'name': 'Финансовая помощь',
        'uploads': 'img/professions/consultant_money.jpg'
    },
    {
        'name': 'Бокс',
        'uploads': 'img/professions/traner_box.jpg'
    },
    {
        'name': 'Фитнес',
        'uploads': 'img/professions/fitness.jpg'
    },
    {
        'name': 'Красота и гигиена',
        'uploads': 'img/professions/styleman.jpg'
    },
    {
        'name': 'Фотосъемки',
        'uploads': 'img/professions/photographer.jpg'
    }
]

SERVICES = [
    {
        'id': i,
        'job': job['name'],
        'img': job['uploads'],
        'about': f'you can to do {i}',
        'age': random.randint(20, 35),
        'sex': random.randint(0, 2),  # 0 - women, 1 - men, 2 - man or woman
        'rus_passport': random.randint(0, 1),
        'insurance': random.randint(0, 1),
        'salary': 2000,
        'date_start': "12.10.2023",
        'date_end': "15.10.2023"
    } for i, job in enumerate(JOBS)
]


@require_GET
def home(req):
    search_text = req.GET.get('search', None)
    GET_PARAMS = {
        "search": search_text
    }
    object_list = SERVICES
    if search_text is not None:
        object_list = [service for service in object_list if search_text.lower() in service.get('job').lower()]
    return render(req, 'pages/index.html', {
        'services': object_list,
        'GET_PARAMS': GET_PARAMS
    })


@require_GET
def service(req, service_id):
    try:
        service_id = int(service_id)
    except ValueError:
        service_id = 0
    except IndexError:
        service_id = len(SERVICES) - 1

    service = SERVICES[service_id]
    return render(req, 'pages/service.html', {
        'service': service
    })