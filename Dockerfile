FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app backend ./backend
COPY --chown=app:app Frontend ./Frontend
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app data ./data
COPY --chown=app:app main.py ./

RUN mkdir -p uploads && chown app:app uploads

USER app

EXPOSE 8000

CMD ["python", "main.py"]
