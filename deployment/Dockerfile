FROM python:3.9

LABEL Author Elfsong

ADD ./luna /project/luna

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH=“${PATH}:/root/.local/bin”

WORKDIR /project/luna

RUN /usr/local/bin/pip3 install --upgrade pip
RUN /usr/local/bin/pip3 install -r requirements.txt

EXPOSE 9000
HEALTHCHECK CMD curl --fail http://localhost:9000/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=9000", "--server.address=0.0.0.0"]