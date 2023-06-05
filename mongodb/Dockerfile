FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY [ "mongodb/requirements.txt", "../ugc_api/src/core/config.py", "../ugc_api/src/models/ugc_model.py", "./" ]

RUN \
    mkdir -p /app \
    && groupadd -r web && useradd -d /app -r -g web web \
    # && mv mongo_click_etl.py /app/mongo_click_etl.py \
    && mv config.py /app/config.py \
    && mv ugc_model.py /app/ugc_model.py \
    && chown web:web -R /app \
    && python -m pip install --upgrade pip \
    && pip install --upgrade wheel \
    && python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8089

WORKDIR /app

USER web

# ENTRYPOINT python mongo_click_etl.py
