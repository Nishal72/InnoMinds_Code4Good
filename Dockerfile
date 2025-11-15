FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean

# Copy requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port used inside container
EXPOSE 8000

# Gunicorn command (docker-compose overrides if needed)
CMD ["gunicorn", "MoLenerzi.wsgi:application", "--bind", "0.0.0.0:8000"]
