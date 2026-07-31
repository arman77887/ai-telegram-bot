FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ ffmpeg tesseract-ocr && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p backups logs
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
