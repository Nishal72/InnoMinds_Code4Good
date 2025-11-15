FROM python:3.10-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Run collectstatic inside the container
RUN python manage.py collectstatic --noinput

# Expose Django internal port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "MoLenerzi.wsgi:application", "--bind", "0.0.0.0:8000"]
