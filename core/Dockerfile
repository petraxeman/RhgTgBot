# --- Builder layer ---
FROM python:3.12-slim as builder

RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends git gcc build-essential \
    && apt-get clean \
    && git config --global http.proxyAuthMethod 'basic'

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



# --- Runtime layer ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV APP_MODULE=main:app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4

EXPOSE 8000

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . .

ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
