# 🏥 Projet Healthcare - Migration de données & Base NoSQL Sécurisée

Ce projet permet de déployer de manière entièrement automatisée une base de données MongoDB sécurisée sous Docker et d'y migrer un jeu de données de santé (*healthcare dataset*) à l'aide d'un script Python autonome.

---

## 📐 Architecture du Projet

* **Base de données :** MongoDB (Conteneur `projet5`)
* **Gestionnaire de dépendances :** `uv` (Astral)
* **Ingestion de données :** Python 3.11 / Pandas / PyMongo (Conteneur `script_migration`)
* **Sécurité :** Création automatique d'un utilisateur applicatif restreint (`app_user` avec rôle `readWrite`) sur la base `healthcare_db`.

---

## 🚀 Prérequis

Avant de commencer, assure-toi d'avoir installé sur ta machine :
* [Docker Engine](https://docs.docker.com/get-docker/) et **Docker Compose V2**
* [Git](https://git-scm.com/)

---

## 🛠️ Installation et Lancement Rapide

### 1. Cloner le dépôt
```bash
git clone [https://github.com/webactiviti/projet_5.git](https://github.com/Webactiviti/projet_5.git)
cd projet_5
```

### 2. Démarrer l'ensemble des services (MongoDB + Migration)
Exécute la commande suivante à la racine du projet :

```bash
sudo docker compose up --build
```

**Que se passe-t-il automatiquement ?**
1. Docker lance le serveur MongoDB avec les droits administrateurs (`root`).
2. Le script de migration Python s'exécute dans un conteneur dédié :
   - Il attend que MongoDB soit prêt.
   - Il crée l'utilisateur applicatif restreint `app_user`.
   - Il nettoie et insère les 10 000 dossiers de patients.
   - Il termine son exécution proprement.

---

## 🧪 Vérification des données & Sécurité

Pour vérifier que les données sont bien présentes et que l'utilisateur applicatif restreint fonctionne, tu peux lancer le script de test local :

```bash
uv run python test_auth.py
```

Ce script vérifie :
- 🟢 **Lecture :** L'accès aux données patients avec `app_user`.
- 🛡️ **Sécurité :** La restriction d'accès aux bases système `admin`.

---

## 📂 Structure du Répertoire

```text
projet_5/
├── docker-compose.yml       # Orchestration des conteneurs (MongoDB & Script)
├── Dockerfile               # Configuration du conteneur Python de migration
├── migrate.py               # Script d'infrastucture et d'ingestion de données
├── test_auth.py             # Script de vérification des droits applicatifs
├── healthcare_dataset.csv   # Données brutes
├── pyproject.toml           # Gestion des dépendances Python (uv)
└── README.md                # Documentation du projet
```
