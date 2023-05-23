FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN \
    mkdir -p /app \
    && groupadd -r web && useradd -d /app -r -g web web \
    && chown web:web -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install locust==2.15.1

EXPOSE 8089

WORKDIR /app

USER web

# ENTRYPOINT locust -f load_test_es.py
