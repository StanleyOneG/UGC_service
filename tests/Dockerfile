FROM python:3.10.8-bullseye

ENV \
    PYTHONPATH=/usr/local/bin/python3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /tests

COPY ./ /tests

RUN \
    groupadd -r tester && useradd -d /tests -r -g tester tester \
    && chown tester:tester -R /tests \
    && pip install --upgrade wheel \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install -r ./tests/requirements.txt


WORKDIR /tests/functional

USER tester

ENTRYPOINT pytest src/
