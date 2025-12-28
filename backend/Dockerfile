FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run expects the service to listen on PORT
ENV PORT=8080
ENV REFRESHED_AT=2025_12_28_V2
EXPOSE 8080

CMD ["functions-framework", "--target=process_query", "--port=8080"]
