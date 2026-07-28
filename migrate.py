import time
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError , OperationFailure
import os
from dotenv import load_dotenv

def lancer_migration():
    client = None

    # Charge les variables depuis le fichier .env s'il existe
    load_dotenv()

    # Récupération des variables d'environnement
    MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_db")

    # On conserve quote_plus uniquement pour la chaîne URI si besoin
    ADMIN_USER_URI = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
    ADMIN_PASS_URI = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "adminpass")
    

    APP_USER = os.getenv("APP_USER_USERNAME", "app_user")
    APP_PASS = os.getenv("APP_USER_PASSWORD", "userpass")

    # Boucle de retentative pour attendre que MongoDB soit 100% prêt
    max_retries = 10
    print("⏳ Attente du démarrage de MongoDB...")
    
    for i in range(max_retries):
        try:
            # URI Administrateur
            uri_admin = f"mongodb://{ADMIN_USER_URI}:{ADMIN_PASS_URI}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
            client = MongoClient(uri_admin)
            client.admin.command('ping')
            print("✅ Connexion réussie à MongoDB !")
            break
        except ConnectionFailure:
            print(f"🔄 MongoDB n'est pas encore prêt ({i+1}/{max_retries}). Retentative dans 2s...")
            time.sleep(2)
    else:
        print("❌ Erreur : Impossible de joindre MongoDB après plusieurs tentatives.")
        return

    try:
        # Accès à la base de données et à la collection
        db = client[DB_NAME]
        collection = db['patients']
        
        # --- CRÉATION DE L'UTILISATEUR APPLICATIF SÉCURISÉ ---
        existing_users = db.command("usersInfo")["users"]
        if not any(u["user"] == APP_USER for u in existing_users):
            print(f"🔑 Création de l'utilisateur applicatif '{APP_USER}' sur la base ...")
            db.command("createUser", APP_USER, 
                       pwd=APP_PASS, 
                       roles=[{"role": "readWrite", "db": DB_NAME}])
            print("🔑 Utilisateur créé avec succès.")
        else:
            print(f"🔑 L'utilisateur applicatif '{APP_USER}' existe déjà.")
            
        # --- LECTURE ET INSERTS ---
        df = pd.read_csv('healthcare_dataset.csv', parse_dates=['Date of Admission', 'Discharge Date'])
        df['Name'] = df['Name'].str.title()
        
        data_dict = df.to_dict(orient='records')
        collection.delete_many({}) 
        result = collection.insert_many(data_dict)
        
        print(f"🎉 Succès ! {len(result.inserted_ids)} dossiers de patients importés avec succès.")

    except FileNotFoundError:
        print("❌ Erreur : Le fichier 'healthcare_dataset.csv' est introuvable dans le conteneur.")
    except PyMongoError as e:
        print(f"⚠️ Une erreur spécifique à MongoDB est survenue : {e}")
    except Exception as e:
        print(f"❓ Une autre erreur inattendue est survenue : {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    lancer_migration()
