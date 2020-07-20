FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gettext python3-dev libpq-dev

RUN mkdir /dj-chat
#设置工作目录
WORKDIR /dj-chat
#将当前目录加入到工作目录中
ADD . /dj-chat

RUN pip install -r /dj-chat/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN python manage.py migrate

EXPOSE 80 8001 8000
