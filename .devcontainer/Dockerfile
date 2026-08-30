FROM ubuntu:22.04

WORKDIR /workspace

# Install system dependencies including Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    postgresql-client \
    git \
    curl \
    nodejs \
    npm \
    make \
    && rm -rf /var/lib/apt/lists/* 

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxrandr2 \
    libxext6 \
    libxss1 \
    libgbm1 \
    fonts-liberation \
    libcups2 \
    libcairo2 \
    libpango-1.0-0 \
    libdbus-1-3 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/* 

# Install Python dependencies
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (for E2E tests)
RUN playwright install chromium

# Create non-root user for development
RUN useradd -m -s /bin/bash dev
USER dev
