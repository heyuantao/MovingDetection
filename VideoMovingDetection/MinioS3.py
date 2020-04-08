# -*- coding: utf-8 -*-
import boto
import boto.s3.connection
from boto.s3.key import Key
import logging 
import sys
import os

logger = logging.getLogger('MinioS3')

class MinioS3:
    def __init__(self, host = "", port = 80, access_key = "", secret_key = ""):
        self.host = host
        self.port = port
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = None

    def setBucket(self,bucketName = ""):
        self.conn = boto.connect_s3(
            aws_access_key_id = self.access_key, aws_secret_access_key = self.secret_key,
            host = S3_HOST, port = S3_PORT, is_secure=False, calling_format = boto.s3.connection.OrdinaryCallingFormat(),
            )
        oneBucket = self.conn.get_bucket(bucketName)
        self.bucket = oneBucket

    def uploadFile(self,filePath,fileName):
        if self.bucket == None:
            logger.info("Bucket not set !")
            return
        if os.path.exists(filePath):
            oneObject = Key(self.bucket)
            oneObject.name = fileName
            oneObject.set_contents_from_filename(filePath)
    
def testCode():
    ###########需要初始化的环境变量############################
    S3_HOST = os.getenv("S3_HOST", default="")
    S3_PORT = os.getenv("S3_PORT", default=0)
    S3_BUCKT = os.getenv("S3_BUCKT", default="")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", default="")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", default="")
    ##########################################################

    s3Client = MinioS3(host=S3_HOST, port=S3_PORT, access_key=S3_ACCESS_KEY, secret_key= S3_SECRET_KEY)
    s3Client.setBucket(bucketName= S3_BUCKT)
    s3Client.uploadFile("run.py","run.py")

if __name__=="__main__":
    testCode()