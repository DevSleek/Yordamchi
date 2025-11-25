FROM python:3.10-slim

WORKDIR /app

# system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user (optional)
RUN useradd -m botuser
USER botuser

CMD ["python", "bot/main.py"]
