# KN SHOP — Bot Telegram | Image pour déploiement 24/7
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .

# Définir BOT_TOKEN dans les variables d'environnement du déploiement
CMD ["python", "-u", "bot.py"]
