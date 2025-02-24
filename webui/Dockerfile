# syntax=docker/dockerfile:1

FROM python:3.12.2-slim

WORKDIR /app

COPY requirements .
RUN pip install -r requirements

COPY . .

ENV FLASK_APP=webui
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "8000"]
