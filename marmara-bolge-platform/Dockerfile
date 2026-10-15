FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m platform && mkdir -p /app/instance && chown -R platform /app/instance
USER platform
VOLUME ["/app/instance"]
EXPOSE 8000
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8000", "--threads=8", "wsgi:app"]
