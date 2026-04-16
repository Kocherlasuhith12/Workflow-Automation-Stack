FROM python:3.11-slim

WORKDIR /app

# FIX: copy requirements FIRST so pip install is cached separately
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the code
COPY . .

# Default command (overridden per service in docker-compose.yml)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]