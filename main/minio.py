from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *
from rest_framework import status


def InternalSaveFileS3(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object(
            bucket_name='services',
            object_name=image_name,
            data=file_object,
            length=file_object.size
        )
        return f"http://localhost:9000/services/{image_name}"
    except Exception as e:
        return {"errors": str(e)}


def SavePictureMinio(new_service, image):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    if not client:
        raise Response({"detail": "Произошла ошибка, попробуйте загрузить фото еще раз"},
                       status=status.HTTP_400_BAD_REQUEST)

    if not client.bucket_exists('services'):
        client.make_bucket('services')

    new_service_id = new_service.id
    image_name = f"service{new_service_id}.jpg"

    if not image:
        return Response({"error": "Нет файла для изображения услуги."})

    result = InternalSaveFileS3(image, client, image_name)

    if 'errors' in result:
        return Response(result)

    new_service.img = result
    new_service.save()

    return Response({"detail": "Фотография была успешно добавлена в хранилище."}, status=status.HTTP_200_OK)


def DeletePictureMinio(service):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    if not client:
        raise Response({"detail": "Произошла ошибка, попробуйте загрузить фото еще раз."},
                       status=status.HTTP_400_BAD_REQUEST)

    if not client.bucket_exists('services'):
        client.make_bucket('services')

    service_id = service.id
    object_name = f"service{service_id}.jpg"
    bucket_name = "services"

    errors = client.remove_object(bucket_name, object_name)

    if errors:
        return Response({"errors": str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Фотография была успешно удалена из хранилища"}, status=status.HTTP_204_NO_CONTENT)


def GetPictureMinio(service_id):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    bucket_name = 'services'
    object_name = f'service{service_id}.jpg'
    try:
        response = client.get_object(bucket_name, object_name)
        return response.read()
    except Exception as e:
        raise e