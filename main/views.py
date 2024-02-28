from django.views.decorators.http import require_GET
from django.shortcuts import render
from .models import Services




@require_GET
def home(req):
    search_text = req.GET.get('search', None)
    GET_PARAMS = {
        "search": search_text
    }
    object_list = SERVICES
    if search_text is not None:
        object_list = [service for obj in object_list if search_text.lower() in obj.get('job').lower()]
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