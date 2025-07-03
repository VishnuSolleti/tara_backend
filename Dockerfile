# FROM python:3.12

# # Install system dependencies including wkhtmltopdf
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     curl \
#     wkhtmltopdf \
#     xfonts-base \
#     fontconfig \
#     libjpeg62-turbo \
#     libxrender1 \
#     && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# # Set working directory
# WORKDIR /app

# # Upgrade pip and install Python dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # Copy project code
# COPY . .

# # Expose the port your app runs 
# EXPOSE 8000

# # Start the Django app with Gunicorn
# CMD ["gunicorn", "Tara.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=2"]
# ---------- STAGE 1: Builder ----------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---------- STAGE 2: Runtime ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install runtime dependencies only (optional: add curl, netcat, etc. if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Optional: expose port (for dev/testing)
EXPOSE 8000

# Health check (optional but recommended)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 CMD curl --fail http://localhost:8000/ || exit 1

# Start the app with Gunicorn
CMD ["gunicorn", "Tara.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=2"]
