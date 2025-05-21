# Используем официальный образ Python с ffmpeg
FROM python:3.10-slim

# Устанавливаем ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запускаем сервер
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "10000"]
