import boto3
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()

class Bucket:
    """CDN Bucket manager

    init method creates connection.
    """

    def __init__(self):
        session = boto3.session.Session()
        self.connection = session.client(
            service_name= settings.AWS_SERVICE_NAME,
            aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url= settings.AWS_S3_ENDPOINT_URL,
        )

    def get_object(self):
        result = self.connection.list_objects_v2(Bucket= os.getenv('AWS_STORAGE_BUCKET_NAME'))
        if result['KeyCount']:
            return result['Contents']
        else:
            return None

    def delete_object(self, key):
        self.connection.delete_object(Bucket= os.getenv('AWS_STORAGE_BUCKET_NAME'), Key=key)
        return True

    def rename_object(self, key, new_name):
        self.connection.copy_object(
            Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'),
            CopySource={'Bucket': os.getenv('AWS_STORAGE_BUCKET_NAME'), 'Key': key},
            Key=new_name,
        )
        self.connection.delete_object(
            Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'),
            Key=key
        )
        return True
