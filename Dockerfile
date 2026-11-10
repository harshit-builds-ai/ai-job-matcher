FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY examples ./examples

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "jobmatch.api:app", "--host", "0.0.0.0", "--port", "8000"]
