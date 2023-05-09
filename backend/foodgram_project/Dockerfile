# Создать образ на основе базового слоя python (там будет ОС и интерпретатор Python).
# 3.7 — используемая версия Python.
# slim — обозначение того, что образ имеет только необходимые компоненты для запуска,
# он не будет занимать много места при развёртывании.
FROM python:3.10-slim

# Запустить команду создания директории внутри контейнера
RUN mkdir /app
RUN mkdir /app/foodgram_project

# Скопировать с локального компьютера файл зависимостей
# в директорию /app.
COPY requirements.txt /app

#решает проблему с pg_config
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Выполнить установку зависимостей внутри контейнера.
RUN pip3 install -r /app/requirements.txt --no-cache-dir

# Скопировать содержимое директории /api_yamdb c локального компьютера
# в директорию /app.
COPY . /app/foodgram_project

# Сделать директорию /app рабочей директорией. 
WORKDIR /app/foodgram_project

# Выполнить запуск сервера разработки при старте контейнера.
CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0:8000" ] 