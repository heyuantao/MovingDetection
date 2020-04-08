FROM ubuntu:18.04

###This part is use to set time zone ########
ENV TZ=Asia/Shanghai
RUN sed -i s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g /etc/apt/sources.list
RUN echo $TZ > /etc/timezone && apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean
ENV LANG C.UTF-8
ENV LC_CTYPE en_US.UTF-8
###  set timezone end ###

RUN apt-get update && apt-get install -y locales &&  locale-gen zh_CN.UTF-8
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list  && echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8

###   the program   ###
COPY ./ /app/MovingDetection/
WORKDIR /app/MovingDetection/
RUN bash /app/MovingDetection/docker/install/install.sh


WORKDIR /app/MovingDetection/VideoMovingDetection/

#CMD python3 run.py

ENTRYPOINT  ["bash","/app/MovingDetection/docker/run.sh"]
