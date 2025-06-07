FROM python:3.12-slim
# python:3.12-slim

RUN apt-get update --fix-missing && \
    apt-get install git -y \
    && apt-get clean \
    && git config --global http.proxyAuthMethod 'basic'

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT python main.py