# Använd officiell Python-baserad image
FROM python:3.9-slim

# Skapa arbetskatalog
WORKDIR /app

# Kopiera kravfiler först för att utnyttja Docker cache
COPY requirements.txt .

# Installera beroenden
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera resten av filerna
COPY . .

# Exponera port
EXPOSE 5000

# Kör applikationen
CMD ["python", "app.py"]