FROM harbor.syslab.org/library/pythoncv2

RUN mkdir /code
COPY CephS3.py /code/
COPY run.py /code/

WORKDIR /code/

CMD python run.py
