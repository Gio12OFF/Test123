FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system streamprobe && adduser --system --ingroup streamprobe streamprobe
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install ".[api]"

USER streamprobe
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"
CMD ["uvicorn", "streamprobe.api:app", "--host", "0.0.0.0", "--port", "8000"]
