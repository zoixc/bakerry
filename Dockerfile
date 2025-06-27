# Используем slim-базу Python
FROM python:3.11-slim

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend-код
COPY backend/app /app/app

# Копируем frontend (один HTML) в static-папку backend'а
COPY frontend/index.html /app/app/static/index.html

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
