FROM python:3.5
EXPOSE 5000
ENV TENSORFLOW_VERSION 0.10.0rc0
RUN pip --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-${TENSORFLOW_VERSION}-cp35-cp35m-linux_x86_64.whl
ADD requirements.txt /
RUN pip --no-cache-dir install -r requirements.txt
#ADD build *.py shared /
ADD *.py bin hypergan  /
ENTRYPOINT ["python3", "hypergan"]
