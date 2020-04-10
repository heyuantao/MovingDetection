# -*- coding: utf-8 -*-
from datetime import datetime
from boto.s3.key import Key
import time
import boto
import boto.s3.connection
import logging 
import sys
import os
import traceback

logger = logging.getLogger('Bucket Cleaner')
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class MinioS3:
    def __init__(self, host = "", port = 80, access_key = "", secret_key = ""):
        self.host = host
        self.port = port
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = None

    def getBucket(self,bucketName):
        self.conn = boto.connect_s3(
            aws_access_key_id = self.access_key, aws_secret_access_key = self.secret_key,
            host = self.host, port = self.port, is_secure=False, calling_format = boto.s3.connection.OrdinaryCallingFormat(),
            )
        oneBucket = self.conn.get_bucket(bucketName)
        self.bucket = oneBucket
        return self.bucket


def main():
    ###########需要初始化的环境变量############################
    S3_HOST = os.getenv("S3_HOST", default="")
    S3_PORT = os.getenv("S3_PORT", default=0)
    S3_BUCKET = os.getenv("S3_BUCKET", default="")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", default="")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", default="")
    ##########################################################


    if (S3_HOST == "") or (S3_PORT == 0) or (S3_BUCKET == "") or (S3_ACCESS_KEY == "") or (S3_SECRET_KEY == ""):
        logger.warning("Variable is not set correctly !")
        return

    logger.info("Begin check if file have been created more than two day !")
    client = MinioS3(host=S3_HOST, port=S3_PORT, access_key=S3_ACCESS_KEY, secret_key= S3_SECRET_KEY)
    bucket = client.getBucket(S3_BUCKET)

    numberOfFileDelete = 0
    for key in bucket.list():
        modifiedTime = time.strptime(key.last_modified[:19], '%Y-%m-%dT%H:%M:%S')
        modifiedDataTime = datetime.fromtimestamp(time.mktime(modifiedTime))
        dayPassed = (datetime.now()-modifiedDataTime).days
        if dayPassed > 2:        #delete the file which has created more than two day
            key.delete()
            numberOfFileDelete = numberOfFileDelete+1
    if numberOfFileDelete >0:
        logger.info("{number} file has been delete !".format(number=numberOfFileDelete))
    else:
        logger.info("no file delete !")
    logger.info("Delete job finished !")
        

if __name__=="__main__":
    sleep_time = 1*60*60
    logger.info("Build at 2020-04-08 !")
    while True:
       try:
          main()
          time.sleep(sleep_time)
       except Exception as e:
          logger.info("Exception Happen !")
          logger.info(traceback.format_exc())
          time.sleep(sleep_time)
          
