from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticS3Boto3Storage(S3Boto3Storage):
    """
    Extend S3Boto3Storage to store the static assets in a different location.
    """
    location = settings.AWS_STATIC_LOCATION


class MediaS3Boto3Storage(S3Boto3Storage):
    """
    Extend S3Boto3Storage to store the media assets in a different location.
    """
    location = settings.AWS_MEDIA_LOCATION
    file_overwrite = False
