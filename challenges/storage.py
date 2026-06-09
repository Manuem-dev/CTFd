from storages.backends.s3boto3 import S3Boto3Storage

class SupabaseStorage(S3Boto3Storage):
    # Désactive la signature d'URL pour que les liens soient publics, directs et permanents
    querystring_auth = False
    file_overwrite = False