FROM python:3.11-slim

WORKDIR /app

# Installation directe de uv via pip
RUN pip install --no-cache-dir uv

# Copie des fichiers de configuration uv
COPY pyproject.toml uv.lock ./

# Installation des dépendances dans le conteneur via uv
RUN uv pip install --system -r pyproject.toml

# Copie des scripts et du jeu de données
COPY migrate.py .
COPY healthcare_dataset.csv .
COPY test_auth.py .

# Commande de lancement
CMD ["python", "migrate.py"]
