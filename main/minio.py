from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *
from rest_framework import status
import uuid


def InternalSaveFileS3(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object(
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
            object_name=image_name,
            data=file_object,
            length=file_object.size
        )
        return f"http://localhost:9000/{settings.AWS_STORAGE_BUCKET_NAME}/{image_name}"
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

    if not client.bucket_exists(settings.AWS_STORAGE_BUCKET_NAME):
        client.make_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    image_name = str(uuid.uuid4()) + '.jpg'

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

    if not client.bucket_exists(settings.AWS_STORAGE_BUCKET_NAME):
        client.make_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    object_name = service.img.split("/")[-1]
    if object_name == 'default.jpg':
        return

    errors = client.remove_object(settings.AWS_STORAGE_BUCKET_NAME, object_name)

    if errors:
        return Response({"errors": str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Фотография была успешно удалена из хранилища"}, status=status.HTTP_200_OK)


def GetPictureMinio(service):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    if not client:
        raise Response({"detail": "Произошла ошибка, попробуйте загрузить фото еще раз."},
                       status=status.HTTP_400_BAD_REQUEST)

    if not client.bucket_exists(settings.AWS_STORAGE_BUCKET_NAME):
        client.make_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    object_name = service.img.split("/")[-1]

    errors = client.remove_object(settings.AWS_STORAGE_BUCKET_NAME, object_name)

    if errors:
        return Response({"errors": str(errors)}, status=status.HTTP_400_BAD_REQUEST)
    try:
        response = client.get_object(settings.AWS_STORAGE_BUCKET_NAME, object_name)
        return response.read()
    except Exception as e:
        raise e