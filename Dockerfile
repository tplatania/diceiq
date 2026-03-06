FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers=2 --timeout=300 --worker-class=sync diceiq_api:app"]
