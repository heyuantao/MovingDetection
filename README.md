##This is the program for video moving detection
###1 Build The docker
```
docker build -t movingdetection:1.0 .
```

###2 Run The container

####2.1 Run the detection container
```
docker run -d --name="detection" -e MODE="DETECTION" -e S3_HOST="videos3.xxx.org" -e S3_PORT="80" -e S3_BUCKET="moving" -e S3_ACCESS_KEY="xxx" -e S3_SECRET_KEY="xxx" -e RTSP_URL="rtsp://xx:xx@video01e.xx.xx:554/cam/realmonitor?channel=8&subtype=0" -e RTSP_NAME="xxx" movingdetection:1.0
```
####2.2 Run the images remove container
```
docker run -d --name="deletion" -e MODE="DELETION" -e S3_HOST="videos3.xxx.org" -e S3_PORT="80" -e S3_BUCKET="moving" -e S3_ACCESS_KEY="xxx" -e S3_SECRET_KEY="xxx" movingdetection:1.0
```
