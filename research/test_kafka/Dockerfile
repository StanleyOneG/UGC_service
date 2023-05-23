FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN \
    mkdir -p /app \
    && groupadd -r web && useradd -d /app -r -g web web \
    && chown web:web -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install -r requirements.txt

EXPOSE 8089

WORKDIR /app

USER web

# ENTRYPOINT locust -f load_test.py
