FROM python:3.12.5-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/usr/src/app