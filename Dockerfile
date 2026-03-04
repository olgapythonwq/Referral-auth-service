FROM python:3.13-slim

# Отключаем буферизацию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Рабочая директория, чтобы копировать зависимости
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock /app/

# Настройка Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# Копируем проект
COPY . /app/

# Создаем пользователя
RUN adduser --disabled-password --no-create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Рабочая директория, чтобы запускать Django
WORKDIR /app/src

CMD ["/usr/local/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1"]
