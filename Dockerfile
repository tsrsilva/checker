# SPDX-FileCopyrightText: 2026 Thiago S. R. Silva, Diego S. Porto
# SPDX-License-Identifier: MIT

# Use an official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file if you have one
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (including LICENSES and configs)
COPY . .

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run the script by default
ENTRYPOINT ["python", "-m", "checker"]

CMD []

