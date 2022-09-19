FROM python:3.9-slim

ENV APP_DIR /app

WORKDIR ${APP_DIR}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN addgroup --system --gid 1001 appuser && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group appuser

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY capstone .

RUN mkdir ${APP_DIR}/staticfiles 

RUN chown -R appuser:appuser ${APP_DIR} && \
    chmod -R 755 ${APP_DIR}

USER appuser
