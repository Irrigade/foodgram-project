# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (нужны для psycopg2 и Pillow)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    musl-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (для админки)
RUN python manage.py collectstatic --noinput

# Запускаем Gunicorn (сервер приложений) на порту 8000
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]