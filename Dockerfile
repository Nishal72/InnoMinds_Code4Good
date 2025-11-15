# Use Python
FROM python:3.10-slim

# Set environment
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Gunicorn (production server)
CMD ["gunicorn", "MoLenerzi.wsgi:application", "--bind", "0.0.0.0:8000"]
