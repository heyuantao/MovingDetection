docker rmi harbor.syslab.org/videomonitor/deletecron:latest
docker build -t harbor.syslab.org/videomonitor/deletecron:latest .

docker run -d --env BUCKET="images" harbor.syslab.org/videomonitor/deletecron:latest