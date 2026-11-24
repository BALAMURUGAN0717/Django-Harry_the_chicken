# Base Image
FROM python:3.12-slim

# Working Directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/chicken_project

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose default port
EXPOSE 8000

# Run migrations, collect static, and start production WSGI server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn chicken_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120"]
