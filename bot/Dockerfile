FROM python:3.12-slim

RUN apt-get update --fix-missing && apt-get install supervisor -y && apt-get clean

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT supervisord -c /bot/supervisor.conf && python main.py