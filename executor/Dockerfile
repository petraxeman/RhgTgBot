FROM python:3.12-slim

RUN apt-get update --fix-missing && \
    apt-get install git -y \
    && apt-get clean

WORKDIR /executor

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT /executor/entrypoint.sh