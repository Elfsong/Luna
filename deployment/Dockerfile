FROM python:3.9

LABEL Author Elfsong

ADD ./src /project/luna

ENV LANG C.UTF-8
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /project/luna

RUN /usr/local/bin/pip3 install --upgrade pip
RUN /usr/local/bin/pip3 install -r requirements.txt

EXPOSE 7777

# ENTRYPOINT ["python","app.py"]