FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY [ "requirements.txt", "load_test_ch.py", "./" ]

ADD config /app/config


RUN \
    groupadd -r web && useradd -d /app -r -g web web \
    && mv /load_test_ch.py /app/load_test_ch.py \
    && chown web:web -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install -r requirements.txt


EXPOSE 8089

WORKDIR /app

USER web

ENTRYPOINT locust -f load_test_ch.py
