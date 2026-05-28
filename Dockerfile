FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Теперь файл прямо в этой же папке, пишем путь без точек наверх!
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое папки jeb_core внутрь папки /app контейнера
COPY ./jeb_core /app/