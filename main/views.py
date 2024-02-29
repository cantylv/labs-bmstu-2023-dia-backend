from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect
from django.http import Http404

from .models import *
from .cursos import *


@require_GET
def home(req):
    userDraft = Bid.objects.get(pk=1)
    search_text = req.GET.get('search', None)
    GET_PARAMS = {
        "search": search_text
    }
    object_list = Service.objects.filter(status=True).order_by('-salary')
    if search_text is not None:
        object_list = object_list.filter(job__search=search_text)
    return render(req, 'pages/index.html', {
        'services': object_list,
        'GET_PARAMS': GET_PARAMS,
        'countServicesInDraft': userDraft.services.filter(status=True).count(),
    })


@require_GET
def service(req, service_id):
    userDraft = Bid.objects.get(pk=1)
    try:
        service_id = int(service_id)
    except ValueError:
        raise Http404("Услуги с таким идентификатором не существует. Проверьте корректность идентификатора.")
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        raise Http404("Услуги с таким идентификатором не существует.")

    return render(req, 'pages/service.html', {
        'service': service,
        'countServicesInDraft': userDraft.services.filter(status=True).count(),
    })


def deleteService(req, service_id):
    try:
        service_id = int(service_id)
        bid = Bid.objects.get(pk=1)
        bid.services.remove(service_id)
    except ValueError:
        raise Http404("Услуги с таким идентификатором не существует. Проверьте корректность идентификатора.")

    try:
        Service.objects.get(id=service_id)
        deleteServiceByCursor(service_id)
        return redirect('home')
    except Service.DoesNotExist:
        raise Http404("Удалить услугу с таким идентификатором невозможно.")


def draft(req):
    userDraft = Bid.objects.get(pk=1)
    draftServices = userDraft.services.all().filter(status=True)
    return render(req, 'pages/draft.html', {
        'draft': userDraft,
        'draftServices': draftServices,
        'countServicesInDraft': userDraft.services.count()
    })