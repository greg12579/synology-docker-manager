FROM python:3.11-slim

WORKDIR /app

# Install wget and download Docker CLI binary
RUN apt-get update && apt-get install -y wget && \
    wget -qO- https://download.docker.com/linux/static/stable/x86_64/docker-27.4.1.tgz | tar xvz --strip 1 -C /usr/local/bin docker/docker && \
    chmod +x /usr/local/bin/docker && \
    apt-get remove -y wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app_simple.py app.py
COPY templates/ templates/
COPY static/ static/

# Expose port 80
EXPOSE 80

# Run the application
CMD ["python", "app.py"]
