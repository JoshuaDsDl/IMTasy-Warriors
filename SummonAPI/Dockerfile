# Utilisation de l'image officielle de Python
FROM python:3.9-slim

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers nécessaires
COPY requirements.txt ./
COPY data.json ./
COPY main.py ./

# Installation des libs Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port de l'API
EXPOSE 5002

# Lancer l'application
CMD ["python", "-u", "main.py"]
