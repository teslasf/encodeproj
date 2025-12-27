import boto3
import logging
from botocore.exceptions import ClientError
import os

# Configure the logging
logging.basicConfig(filename='s3_errors.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class S3FileClass:
    def __init__(self, app, file):
        self.file = file
        self.app = app
        self.s3 = boto3.client('s3')
        self.bucket_name = os.getenv('BUCKETEER_BUCKET_NAME')

    def get_object_name(self):
        return os.path.basename(self.file)

    def upload_file(self):
        try:
            object_name = self.get_object_name()
            self.s3.upload_file(self.file, self.bucket_name, object_name)
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def get_s3_url(self):
        try:
            object_name = self.get_object_name()
            url = self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name, 'Key': object_name})
            return url
        except ClientError as e:
            logging.error(e)
           