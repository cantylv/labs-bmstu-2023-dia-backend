# Локальная база данных
import random
from django.conf import settings

baseDir = settings.BASE_DIR

# УСЛУГИ
Jobs = [
    {
        'name': 'Программирование',
        'uploads': f'/static/img/services/prog.jpg'
    },
    {
        'name': 'Массаж',
        'uploads': '/static/img/services/massage.jpg'
    },
    {
        'name': 'Сантехнические работы',
        'uploads': '/static/img/services/santechnik.jpg'
    },
    {
        'name': 'Автомойка',
        'uploads': '/static/img/services/wash_car.jpg'
    },
    {
        'name': 'Ветеринария',
        'uploads': '/static/img/services/veterinar.jpg'
    },
    {
        'name': 'Медицина',
        'uploads': '/static/img/services/urolog.jpg'
    },
    {
        'name': 'Репетиторство',
        'uploads': '/static/img/services/teacher.jpg'
    },
    {
        'name': 'Юриспруденция',
        'uploads': '/static/img/services/jurist.jpg'
    },
    {
        'name': 'Охрана и безопасность',
        'uploads': '/static/img/services/security.png'
    },
    {
        'name': 'Аналитика данных',
        'uploads': '/static/img/services/datanal.jpg'
    },
    {
        'name': 'Финансовая помощь',
        'uploads': '/static/img/services/consultant_money.jpg'
    },
    {
        'name': 'Бокс',
        'uploads': '/static/img/services/traner_box.jpg'
    },
    {
        'name': 'Фитнес',
        'uploads': '/static/img/services/fitness.jpg'
    },
    {
        'name': 'Красота и гигиена',
        'uploads': '/static/img/services/styleman.jpg'
    },
    {
        'name': 'Фотосъемки',
        'uploads': '/static/img/services/photographer.jpg'
    }
]

Services = [
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
        'date_start': "12.10.2023 в 18:00",
        'date_end': "15.10.2023 в 15:00"
    } for i, job in enumerate(Jobs)
]

Draft = {
    "services": Services[2:7],
    "date_create": '29.02.2023 в 00:08',
    "date_formation": '-',
    'date_finish': '-',
    'status': 'Черновик',
    'user': 'tussan_pussan',
}