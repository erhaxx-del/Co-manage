# Sunucu ortamları için giriş noktası: waitress-serve --port=8000 wsgi:app  |  gunicorn wsgi:app
from app import uygulama_olustur
app = uygulama_olustur()
