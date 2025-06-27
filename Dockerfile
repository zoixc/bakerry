# Используем Python как базовый образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend-код
COPY backend/app ./app

# Копируем index.html фронтенда в static
COPY frontend/index.html ./app/static/index.html

# Создаём папки для данных
RUN mkdir -p /data/backups && mkdir -p /data

# Указываем рабочую директорию backend
WORKDIR /app/app

# Указываем переменную окружения для корректной работы FastAPI
ENV PYTHONUNBUFFERED=1

# Указываем команду запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
