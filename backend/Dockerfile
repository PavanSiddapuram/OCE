FROM python:3.11-slim

WORKDIR /app

RUN pip install hatchling

COPY pyproject.toml .
RUN pip install -e .

COPY . .

EXPOSE 8000
