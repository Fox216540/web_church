# Используем официальный образ Python
FROM python:3.11-slim

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install -vvv --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .