# -*- coding: utf-8 -*-  
from multiprocessing import Process, Queue
from datetime import datetime
import shutil
import cv2 
import os
import time
import logging
import sys
import traceback
from MinioS3 import MinioS3

QUEUE_LENGTH = 50
CAM_TIME_INTERVAL = 1
IMAGE_DIR = "./images"

logger = logging.getLogger('MovingDetection')
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


class Settings:
    class StorageSettings:
        S3_HOST = ""
        S3_PORT = 0
        S3_BUCKT = ""
        S3_ACCESS_KEY = ""
        S3_SECRET_KEY = ""

    class RTSPSettings:
        RTSP_URL = ""
        RTSP_NAME = ""

    storage = StorageSettings()
    rtsp = RTSPSettings()


def initalizeDir(imageDir):
    if os.path.exists(imageDir):
        shutil.rmtree(imageDir)
    os.mkdir(imageDir)

def imageDifferentRatio(firstImage,secondImage): #this model is test under my experience
    gaussKernel = (21,21)
    delta = 0.1
    firstGray = cv2.cvtColor(firstImage, cv2.COLOR_RGB2GRAY)
    firstGray = cv2.GaussianBlur(firstGray,gaussKernel,delta)
    secondGray = cv2.cvtColor(secondImage, cv2.COLOR_RGB2GRAY)
    secondGray = cv2.GaussianBlur(secondGray,gaussKernel,delta)

    absImage = cv2.absdiff(secondGray,firstGray)

    ret,thrsholdImage = cv2.threshold(absImage,200,255,cv2.THRESH_BINARY) #127
    dilateImage = cv2.dilate(thrsholdImage, None, iterations=2)

    imageHist = cv2.calcHist([dilateImage],[0],None,[2],[0,256])    
    #the white pixel of all pix,the white pix is moving parts of picture
    whiteRatio = float(imageHist[1][0]/(imageHist[0][0]+imageHist[1][0])) *1000 
    #this ratio is too small so multiply by 1000,if this ratio large than 1,which means that something is moving
    return whiteRatio


def  CaptureImageProcess(q,settings):
    while True:
        try:
            queue = q
            capture = cv2.VideoCapture(settings.rtsp.RTSP_URL)
            ret,frame = capture.read()
            if ret == False:
                raise Exception("Error in capture video frame !")
            pre_time = datetime.now()
            while ret:
                ret,frame = capture.read()
                if ret == False:
                    raise Exception("Error in capture video frame !")
                pos_time = datetime.now()
                delta_time = pos_time - pre_time
                if delta_time.seconds > CAM_TIME_INTERVAL:            
                    fileName = pos_time.strftime("%Y%m%d%H%M%S")+".jpg"   
                    filePath = IMAGE_DIR+"/"+fileName
                    if not queue.full():
                        cv2.imwrite(filePath,frame)
                        queue.put(fileName)
                        logger.debug("Save {file} !".format(file = fileName))
                    else:
                        logger.debug("Queue Full !")
                    pre_time = datetime.now()
                        
                #cv2.imshow("frame",frame)       #not display windows        
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
            capture.release()
        except Exception as e:
            logger.error("VideoCatpure Error Happen !")
            logger.debug(traceback.format_exc())
            logger.error("Please check {url} !".format(url = settings.rtsp.RTSP_URL))
            time.sleep(30)

def cleanQueueAndFilesOnErrorHappen(queue):
    while not queue.empty():
        fileName = queue.get()
        filePath = IMAGE_DIR+"/"+fileName
        if os.path.exists(filePath):
            os.remove(filePath)  

def ImageMovingDetectionProcess(q,settings):
    queue = q
    #identityString = rtspName
    identityString = settings.rtsp.RTSP_NAME
    firstImage = None
    secondImage = None

    c3Client = MinioS3(host=settings.storage.S3_HOST, port=settings.storage.S3_PORT, access_key=settings.storage.S3_ACCESS_KEY, secret_key= settings.storage.S3_SECRET_KEY)
    s3Bucket = c3Client.setBucket(bucketName=settings.storage.S3_BUCKT)
    while True:     
        try:
            if not queue.empty():
                fileName = queue.get()
                filePath = IMAGE_DIR+"/"+fileName
                firstImage = secondImage
                secondImage = cv2.imread(filePath)
                if firstImage is None:
                    firstImage = secondImage
                #print "process {file} !".format(file=fullpath)
                movingRatio = imageDifferentRatio(firstImage,secondImage)
                logger.debug("Ratio is:{ratio} (1/1000)".format(ratio=movingRatio))
                
                if os.path.exists(filePath) and movingRatio < 1:
                    #s3FileName = identityString+"_"+fileName
                    #c3Client.uploadFile(filePath,s3FileName)
                    os.remove(filePath)     
                elif os.path.exists(filePath) and movingRatio >= 1:
                    s3FileName = identityString+"_"+fileName
                    c3Client.uploadFile(filePath,s3FileName)
                    os.remove(filePath)    
            else:
                time.sleep(10)
        except Exception as e:
            logger.error("Detection Motion Error Happen !")
            logger.debug(traceback.format_exc())
            logger.error("Clean Queue and restart !")
            if os.path.exists(filePath):
                os.remove(filePath)  
            cleanQueueAndFilesOnErrorHappen(queue)
            time.sleep(10)

def main():
    ###########需要初始化的RTSP的环境变量############################
    RTSP_URL = os.getenv("RTSP_URL", default="")
    RTSP_NAME = os.getenv("RTSP_NAME", default="")
    #############################################################
    ###########需要初始化的S3的环境变量#############################
    S3_HOST = os.getenv("S3_HOST", default="")
    S3_PORT = int(os.getenv("S3_PORT", default=0))
    S3_BUCKET = os.getenv("S3_BUCKET", default="")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", default="")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", default="")
    ############################################################

    if (RTSP_URL == "") or (RTSP_NAME == "") :
        logger.fatal("Environment variable is None ! Please set 'RTSP_URL' 'DVR_NAME' 'RTSP_NAME' !")
        return
    else:
        logger.info("DVR_NAME:{RTSP_NAME} RTSP_URL:{RTSP_URL}".format(RTSP_NAME = RTSP_NAME, RTSP_URL = RTSP_URL))

    if (S3_HOST == "") or (S3_PORT == 0) or (S3_BUCKET == "") or (S3_ACCESS_KEY == "") or (S3_SECRET_KEY == ""):
        logger.fatal("S3 storage params is not set corectly !")
        return
    else:
        logger.info("Use S3 compatible storage with host:{} port:{} bucket:{} access_key:{} secret_key:{} !".format(S3_HOST, S3_PORT, S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY))

    #初始化settings文件
    settings = Settings()
    settings.rtsp.RTSP_NAME = RTSP_NAME
    settings.rtsp.RTSP_URL = RTSP_URL
    settings.storage.S3_HOST = S3_HOST
    settings.storage.S3_PORT = S3_PORT
    settings.storage.S3_BUCKT = S3_BUCKET
    settings.storage.S3_ACCESS_KEY = S3_ACCESS_KEY
    settings.storage.S3_SECRET_KEY = S3_SECRET_KEY

    initalizeDir(IMAGE_DIR)

    imageFileNameQueue = Queue(maxsize = QUEUE_LENGTH)

    producer = Process(target=CaptureImageProcess, args=(imageFileNameQueue,settings))
    consumer = Process(target=ImageMovingDetectionProcess, args=(imageFileNameQueue,settings))

    producer.start() 
    consumer.start()

    producer.join()
    consumer.join()

if __name__=="__main__":
    main()
