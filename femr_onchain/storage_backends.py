from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    def get_created_time(self, name):
        pass

    def get_accessed_time(self, name):
        pass

    def path(self, name):
        pass

    location = 'media'
    files_overwrite = False
