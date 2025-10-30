# Folosește Python 3.11
FROM python:3.11-slim

# Setează folderul de lucru
WORKDIR /app

# Copiază tot codul în container
COPY . .

# Upgrade pip și instalare dependențe
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comanda de pornire a botului
CMD ["python3", "bot.py"]
