# Используем официальный образ Python.
FROM python:3.14.10-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /church

# Зависимости устанавливаются отдельно от исходного кода, чтобы Docker мог
# переиспользовать этот слой при изменениях приложения.
RUN pip install --no-cache-dir poetry==2.5.1
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Application sources live in the repository's church/ directory.  Copy its
# contents into WORKDIR so runtime paths such as /church/manage.py and
# /church/scripts/start-web.sh match docker-compose.yml.
COPY church/ .
