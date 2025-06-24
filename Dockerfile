FROM python:3.12-slim

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Start app using gunicorn
CMD ["gunicorn", "--bind=unix:/app/Tara/Tara.sock", "Tara.wsgi:application"]

