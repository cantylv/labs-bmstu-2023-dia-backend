from django.shortcuts import render
from .models import Services, Draft

def home(req):
    search_text = req.GET.get('search', None)
    GET_PARAMS = {
        "search": search_text
    }
    object_list = Services
    if search_text is not None:
        object_list = [obj for obj in object_list if search_text.lower() == obj['job'].lower()]
    return render(req, 'pages/index.html', {
        'services': object_list,
        'GET_PARAMS': GET_PARAMS,
        'countServicesInDraft': len(Draft.get('services'))
    })


def service(req, service_id):
    currentService = Services[service_id]
    return render(req, 'pages/service.html', {
        'service': currentService,
        'countServicesInDraft': len(Draft.get('services'))
    })


def draft(req):
    return render(req, 'pages/draft.html', {
        'draft': Draft,
        'countServicesInDraft': len(Draft.get('services'))
    })