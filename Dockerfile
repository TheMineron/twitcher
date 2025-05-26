FROM python:3.12

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser && \
    mkdir -p /twitcher/static /twitcher/media && \
    chown -R appuser:appuser /twitcher

WORKDIR /twitcher

COPY --chown=appuser:appuser . .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

USER appuser
