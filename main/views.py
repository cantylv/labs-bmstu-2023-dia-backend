# Для аутентификации/авторизации
from rest_framework.decorators import permission_classes
from .permission import *  # кастомные ограничения на использование api
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser

# Для работы с DRF
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view

# Для работы с БД
from .models import *
from django.forms.models import model_to_dict
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

# Для работы с minio
from .minio import SavePictureMinio, GetPictureMinio, DeletePictureMinio
from django.http import HttpResponse

# Для работы с Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, Parameter, TYPE_OBJECT, TYPE_STRING, IN_QUERY, TYPE_FILE

# Для работы с Redis
import uuid
import datetime
import redis
from django.conf import settings
from .authentication import RedisSessionAuthentication

session_storage = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


# Функции для проверки валидности введеных данных
def validate_service(service_id):
    service = get_object_or_404(Service, pk=service_id)
    return service


########################################    SWAGGER    ################################################################

# Определение параметров для документации Swagger
parameters_get_list_services = [
    Parameter('search', IN_QUERY, description='Поисковый запрос', type=TYPE_STRING)
]

parameters_get_list_bids = [
    Parameter('date_start', IN_QUERY, description='Начальный диапазон даты формирования заявки', type=TYPE_STRING),
    Parameter('date_end', IN_QUERY, description='Конечный диапазон даты формирования заявки', type=TYPE_STRING),
    Parameter('status', IN_QUERY, description='Запрашиваемый статус заявки', type=TYPE_STRING)
]

########################################   SWAGGER.ERRORS   ###########################################################
# Неправильно создается услуга

# Определение ошибок/предупреждений при неправильных запросах
data_not_found = 'Запрашиваемые данные не найдены'
bad_user_permission = 'Недостаточно прав на совершение действия'
error_change_service = 'Ошибка изменения услуги'
error_add_service = 'Ошибка создания услуги'
error_add_service_in_bid = 'Ошибка добавления услуги в заявку'
error_service_already_in_bid = 'Запрашиваемая услуга уже находится в заявке'
error_service_not_in_bid = 'Удаляемая услуга не находится в заявке'
error_incorrect_status = 'Передан некорретный статус заявки'
error_bid_doesnt_exist = 'Такой заявки не существует'
error_user_already_exist = 'Такой пользователь уже зарегистрирован'
error_bad_request = 'Ошибки в запросе'
error_wrong_credentials = 'Неверный пароль или логин'
remove_success = 'Данные были успешно удалены'
success_authorization = 'Успешная авторизация'
success_registration = 'Успешная регистрация'
success_logout = 'Пользовательская сессия завершена успешно'
success_change_data = 'Данные были успешно изменены'
success_add_data = 'Данные были успешно добавлены'


########################################################################################################################


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func

    return decorator


class ServiceList(APIView):
    model_class = Service
    serializer_class = ServiceSerializer
    authentication_classes = [RedisSessionAuthentication]

    ### Получение списка услуг. Это может сделать любой пользователь, в том числе незарегистрированный ###
    @swagger_auto_schema(
        operation_description="Получение списка услуг. Это может сделать любой пользователь, в том числе незарегистрированный. Список услуг сортируется автоматически по убыванию заработной платы",
        responses={200: serializer_class(many=True)},
        manual_parameters=parameters_get_list_services
    )
    def get(self, req):
        object_list = self.model_class.objects.filter(status=True).order_by('-salary')
        search_text = req.GET.get('search', None)
        date_start = req.GET.get('date_start', None)
        date_end = req.GET.get('date_end', None)
        salary_start = req.GET.get('salary_start', None)
        salary_end = req.GET.get('salary_end', None)

        # полнотекстовый поиск (ищет только по словам, регистр значения не имеет)
        if search_text is not None:
            object_list = object_list.filter(job__search=search_text)

        if date_start is not None:
            object_list = object_list.filter(date_start__gte=date_start)
        if date_end is not None:
            object_list = object_list.filter(date_end__lte=date_end)

        if salary_start is not None:
            object_list = object_list.filter(salary__gte=salary_start)
        if salary_end is not None:
            object_list = object_list.filter(salary__lte=salary_end)

        serializer = self.serializer_class(object_list, many=True)
        response_data = {
            "services": serializer.data
        }
        if req.user != AnonymousUser:
            draft = Bid.objects.filter(Q(status='draft') & Q(user=req.user))
            if draft.exists():
                response_data["draft_id"] = draft[0].id
        return Response(response_data, status=status.HTTP_200_OK, content_type='application/json')

    ### Создание услуги админом ###
    @swagger_auto_schema(
        request_body=serializer_class,
        operation_description="Создание услуги админом",
        responses={
            201: serializer_class,
            400: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=error_add_service)}),
            403: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=bad_user_permission)})
        })
    @method_permission_classes([IsAdmin])
    def post(self, req):
        uploaded_file = None
        if 'img' in req.data:
            uploaded_file = req.data['img']
            req.data['img'] = 'pass'

        serializer = self.serializer_class(data=req.data)
        if serializer.is_valid():
            service = serializer.save()
            service.status = True
            service.save()
            result = SavePictureMinio(service, uploaded_file)
            if 'errors' in result.data:
                return result
            return Response(serializer.data, status=status.HTTP_201_CREATED, content_type='application/json')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


class ServiceDetail(APIView):
    model_class = Service
    serializer_class = ServiceSerializer

    ### Получение услуги всеми пользователями системы ###
    @swagger_auto_schema(
        operation_description="Получение услуги всеми пользователями: от анономиного до админа",
        responses={
            200: serializer_class,
            404: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=data_not_found)
                }
            )
        })
    def get(self, req, service_id):
        service = validate_service(service_id)
        if not service.status:
            return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND,
                            content_type='application/json')
        serializer = self.serializer_class(service)
        return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')

    ### Изменение услуги админом ###
    @swagger_auto_schema(
        request_body=serializer_class,
        operation_description="Изменение услуги админом",
        responses={
            200: serializer_class,
            400: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=error_change_service)}),
            403: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=bad_user_permission)}),
            404: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=data_not_found)})
        })
    @method_permission_classes([IsAdmin])
    def put(self, req, service_id):
        service = validate_service(service_id)
        if not service.status:
            return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)

        uploaded_file = None
        if 'img' in req.data:
            uploaded_file = req.data['img']
            req.data['img'] = service.img

        serializer = self.serializer_class(service, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if uploaded_file:
                DeletePictureMinio(service)
                result = SavePictureMinio(service, uploaded_file)
                if 'errors' in result.data:
                    return result
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    ### Удаление услуги админом ###
    @swagger_auto_schema(
        request_body=serializer_class,
        operation_description="Удаление услуги админом",
        responses={
            204: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=remove_success)}),
            403: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=bad_user_permission)}),
            404: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=data_not_found)})
        })
    @method_permission_classes([IsAdmin])
    def delete(self, req, service_id):
        service = validate_service(service_id)
        if not service.status:
            return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)

        service.status = False
        # если нужно будет удалить из хранилища фотографию, можно воспользоваться этим методом
        # result = DeletePictureMinio(service)
        # if 'errors' in result.data:
        #     return result
        service.save()

        services = self.model_class.objects.filter(status=True)
        serializer = self.serializer_class(services)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


### Добавление услуги в заявку. Доступно только пользователю ###
@swagger_auto_schema(
    method='POST',
    request_body=ServiceSerializer,
    operation_description="Добавление услуги в заявку. Доступно только пользователю",
    responses={
        201: ServiceSerializer,
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_add_service_in_bid)}),
        404: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=data_not_found)})
    })
@api_view(['POST'])
@permission_classes([IsUser])
def AddServiceToDraft(req, service_id):
    service = validate_service(service_id)
    if not service.status:
        return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND, content_type='application/json')

    bid = Bid.objects.filter(user=req.user).filter(status='draft')
    if not bid:
        bid = Bid.objects.create(user=req.user)  # если заявки с id == bid_id не было, то мы создаем новую заявку
    else:
        bid = bid[0]

    if service in bid.services.all():
        return Response({"detail": error_service_already_in_bid}, status=status.HTTP_400_BAD_REQUEST,
                        content_type='application/json')
    else:
        bid.services.add(service)
        serializer = BidSerializer(bid)
        return Response(serializer.data, status=status.HTTP_201_CREATED, content_type='application/json')


### Удаление услуги из заявки. Доступно только пользователю ###
@swagger_auto_schema(
    method='DELETE',
    operation_description="Удаление услуги из заявки. Доступно только пользователю",
    responses={
        204: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=remove_success)}),
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_service_not_in_bid)}),
        404: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=data_not_found)})
    })
@api_view(['DELETE'])
@permission_classes([IsUser])
def DeleteServiceFromDraft(req, service_id, bid_id):
    service = validate_service(service_id)
    if not service.status:
        return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)

    try:
        bid = get_object_or_404(Bid, pk=bid_id)
    except ValueError:
        return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST,
                        content_type='application/json')

    isNotValidDraft = bid.status != "draft" or (bid.user.id != req.user.id and bid.status == 'draft')
    if isNotValidDraft:
        return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST,
                        content_type='application/json')

    if service in bid.services.all():
        bid.services.remove(service)
        serializer = BidSerializer(bid)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"detail": error_service_not_in_bid}, status=status.HTTP_200_OK)


class BidList(APIView):
    model_class = Bid
    serializer_class = BidSerializer
    permission_classes = ([IsAuth])

    ### Получение списка заявок. Запрашивается список заявок ###
    ### В котором находится одна заявка-черновик (при наличии таковой). Доступно только авторизованному пользователю ###
    @swagger_auto_schema(
        operation_description="""Получение списка заявок. Пользователь запрашивает либо список сформированных заявок, либо 
        список, в котором находится одна заявка-черновик (при наличии таковой). Доступно только авторизованному пользователю""",
        responses={
            200: serializer_class(many=True),
            400: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=error_bid_doesnt_exist)})
        },
        manual_parameters=parameters_get_list_services
    )
    def get(self, req):
        try:
            session_id = req.COOKIES.get('session_id')

            user_id = int(session_storage.get(session_id))
            user = CustomUser.objects.get(pk=user_id)

            is_moderator = user.is_superuser
        except CustomUser.DoesNotExist:
            return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST)

        date_start = req.GET.get('date_start', None)
        date_end = req.GET.get('date_end', None)
        get_status = req.GET.get('status', None)
        username = req.GET.get('username', None)

        if is_moderator:
            object_list = self.model_class.objects.exclude(Q(status='draft') | Q(status='deleted'))

            if get_status not in ('formed', 'rejected', 'completed', None):
                return Response({"detail": error_incorrect_status}, status=status.HTTP_400_BAD_REQUEST)
        else:
            object_list = self.model_class.objects.exclude(status='deleted').filter(user=user)

            if get_status not in ('formed', 'draft', 'rejected', 'completed', None):
                return Response({"detail": error_incorrect_status}, status=status.HTTP_400_BAD_REQUEST)

        if get_status:
            object_list = object_list.filter(status=get_status)
        if date_start:
            object_list = object_list.filter(date_formation__gte=date_start)
        if date_end:
            object_list = object_list.filter(date_formation__lte=date_end)
        if username:
            object_list = object_list.filter(user__username=username)

        serializer = self.serializer_class(object_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BidDetail(APIView):
    model_class = Bid
    serializer_class = BidSerializer
    permission_classes = ([IsAuth])

    # Получение данных заявки менеджером или админом

    @swagger_auto_schema(
        operation_description="Получение заявки менеджером или админом",
        responses={
            204: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=remove_success)}),
            400: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=error_bid_doesnt_exist)}),
            403: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=bad_user_permission)}),
            404: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=data_not_found)}),
        })
    def get(self, req, bid_id):
        try:
            session_id = req.COOKIES.get('session_id')

            user_id = int(session_storage.get(session_id))
            user = CustomUser.objects.get(pk=user_id)

            is_moderator = user.is_superuser
        except CustomUser.DoesNotExist:
            return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST)

        bid = get_object_or_404(self.model_class, pk=bid_id)

        if is_moderator:
            if bid.status not in ('formed', 'rejected', 'completed'):
                return Response({"detail": error_bid_doesnt_exist}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if bid.status not in ('formed', 'draft', 'rejected', 'completed'):
                return Response({"detail": error_bid_doesnt_exist}, status=status.HTTP_400_BAD_REQUEST)
            if bid.user.id != user.id:
                return Response({"detail": bad_user_permission}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(bid)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Удаление заявки
    @method_permission_classes([IsUser])
    def delete(self, req, bid_id):
        try:
            bid = Bid.objects.get(pk=bid_id)
            if bid.user is not req.user:
                return Response({"detail": bad_user_permission}, status=status.HTTP_403_FORBIDDEN)
            bid.status = 'deleted'
            bid.save()
            return Response({"detail": remove_success}, status=status.HTTP_204_NO_CONTENT)
        except Bid.DoesNotExist:
            return Response({"detail": data_not_found}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST)


# Изменение статуса услуги (завершение/отклонение) модератором
@swagger_auto_schema(
    method='PUT',
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'status': Schema(type=TYPE_STRING, description='Новый статус заявки')}),
    operation_description="Изменение статуса услуги (завершение/отклонение) авторизованным пользователем",
    responses={
        200: BidSerializer,
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_incorrect_status)}),
        403: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=bad_user_permission)}),
        404: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=data_not_found)})
    })
@api_view(['PUT'])
@permission_classes([IsAuth])
def ChangeBidStatus(req, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    try:
        session_id = req.COOKIES.get('session_id')

        user_id = int(session_storage.get(session_id))
        if user_id is None:
            return Response({"detail": bad_user_permission}, status=status.HTTP_403_FORBIDDEN)

        user = CustomUser.objects.get(pk=user_id)
        is_moderator = user.is_superuser
    except CustomUser.DoesNotExist:
        return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)

    new_status = req.GET.get('status', None)

    if is_moderator:
        if bid.status != 'formed':
            return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)

        if new_status not in ('rejected', 'completed'):
            return Response({"detail": error_incorrect_status}, status=status.HTTP_400_BAD_REQUEST)

        bid.date_finish = timezone.now()
        bid.moderator = req.user
    else:
        if new_status not in ('formed', 'deleted'):
            return Response({"detail": error_incorrect_status}, status=status.HTTP_400_BAD_REQUEST)
        if bid.user.id != user.id:
            return Response({"detail": bad_user_permission}, status=status.HTTP_403_FORBIDDEN)

        if new_status == 'formed':
            bid.date_formation = timezone.now()

    bid.status = new_status

    bid.save()
    serializer = BidSerializer(bid)

    return Response(serializer.data, status=status.HTTP_200_OK)


# Получение фотографии для услуги
@swagger_auto_schema(
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'img': Schema(type=TYPE_FILE, description='Новое изображение услуги')}),
    operation_description="Получение фотографии для услуги или ее изменение. Получение доступно любому пользователю, регистрация/авторизация необязательны. Изменять фото услуги может только администратор.",
    responses={
        200: success_change_data,
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_change_service)
            }
        ),
        404: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=data_not_found)
            }
        )
    })
class PictureImage(APIView):
    model_class = Service
    serializer_class = ServiceSerializer

    def get(self, req, service_id):
        try:
            file = GetPictureMinio(service_id)
            return HttpResponse(file.read(), content_type="image/jpeg")
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes([IsAdmin])
    def put(self, req, service_id):
        try:
            service = Service.objects.get(pk=service_id)
            file_object = req.data.get('img')
            if file_object:
                DeletePictureMinio(service)
            SavePictureMinio(service, file_object)
            return Response({"detail": success_change_data}, status=status.HTTP_206_PARTIAL_CONTENT)
        except Service.DoesNotExist:
            return Response({"detail": data_not_found}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": error_change_service}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'username': Schema(type=TYPE_STRING, description='Никнейм пользователя'),
            'password': Schema(type=TYPE_STRING, description='Пароль пользователя')
        }),
    operation_description="Авторизация пользователя. Метод принимает никнейм пользователя и пароль для авторизации",
    responses={
        200: success_authorization,
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_bad_request)
            }
        ),
        403: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=bad_user_permission)
            }
        )
    })
@api_view(['POST'])
@permission_classes([IsAnonymous])
def UserLogin(req):
    get_username = req.data.get("username", ' ')
    get_password = str(req.data.get("password", ' '))
    user = authenticate(req, username=get_username, password=get_password)
    if user is not None:
        session_key = str(uuid.uuid4())
        session_storage.set(session_key, user.id)

        response = Response(model_to_dict(user), status=status.HTTP_200_OK)

        # Вычисляем текущую дату и добавляем 14 дней к текущей дате
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=14)
        response.set_cookie("session_id", session_key, expires=expiration_date)  # 14 дней
        return response
    else:
        return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="Выход пользователя из системы. Метод удаляет сессионную cookie из браузера, пользователь больше не может создавать заявки",
    responses={
        200: success_logout,
        400: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=error_bad_request)
            }
        ),
        403: Schema(
            type=TYPE_OBJECT,
            properties={
                'detail': Schema(type=TYPE_STRING, description=bad_user_permission)
            }
        )
    })
@api_view(['POST'])
@permission_classes([IsAuth])
def UserLogout(req):
    session_key = req.COOKIES.get("session_id")
    if session_storage.exists(session_key):
        session_storage.delete(session_key)
        response = Response({'detail': success_logout}, status=status.HTTP_200_OK)
        response.delete_cookie("session_id")
        return response
    return Response({'detail': error_bad_request}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    authentication_classes = []
    permission_classes = [IsAnonymous]

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Регистрация пользователя в системе. Сервер отправляет сессию пользователя и csrf-токен в виде cookies",
        responses={
            200: success_registration,
            400: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=error_bad_request)
                }
            ),
            403: Schema(
                type=TYPE_OBJECT,
                properties={
                    'detail': Schema(type=TYPE_STRING, description=bad_user_permission)
                }
            )
        })
    def create(self, req, *args, **kwargs):
        if self.model_class.objects.filter(username=req.data['username']).exists():
            return Response({'detail': error_user_already_exist}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=req.data)
        if serializer.is_valid():
            is_moderator = serializer.data.get('is_superuser', False)
            response_user = None
            if is_moderator:
                user = CustomUser.objects.create_superuser(**dict(serializer.data))
                response_user = user
                if not is_moderator:
                    user.is_superuser = False
                    user.save()
            else:
                user = CustomUser.objects.create_user(**dict(serializer.data))
                response_user = user

            # сессия пользователя
            session_key = str(uuid.uuid4())
            session_storage.set(session_key, user.id)

            # Вычисляем текущую дату и добавляем 14 дней к текущей дате
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=14)

            response = Response(model_to_dict(response_user), status=status.HTTP_200_OK,
                                content_type='application/json')
            response.set_cookie("session_id", session_key, expires=expiration_date)  # 14 дней

            return response

        return Response({"detail": error_bad_request}, status=status.HTTP_400_BAD_REQUEST)
