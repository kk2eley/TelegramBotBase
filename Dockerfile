FROM python:3.11-slim

# Отключаем создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE 1
# Автоматически выводим логи без буферизации
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache -r /app/requirements.txt

# Копируем весь код в рабочую директорию
COPY bot /app/bot

# Запускаем приложение
CMD ["python", "-m", "bot"]
