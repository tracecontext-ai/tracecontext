FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY tracecontext/ ./tracecontext/

RUN pip install --no-cache-dir ".[db]"

EXPOSE 8000

CMD ["tracecontext", "serve", "--host", "0.0.0.0", "--port", "8000"]
