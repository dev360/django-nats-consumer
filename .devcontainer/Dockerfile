FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.8

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

RUN poetry install --no-root --all-extras

EXPOSE 8000
