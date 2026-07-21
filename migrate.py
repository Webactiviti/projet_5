import time
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

def lancer_migration():
    client = None
    # Boucle de retentative pour attendre que MongoDB soit 100% prêt
    max_retries = 10
    print("⏳ Attente du démarrage de MongoDB...")
    
    for i in range(max_retries):
        try:
            # Note : On utilise 'mongodb' au lieu de 'localhost' dans Docker
            client = MongoClient('mongodb://admin:SuperMotDePasseAdmin123!@mongodb:27017/', serverSelectionTimeoutMS=2000)
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
        db = client['healthcare_db']
        collection = db['patients']
        
        # --- CRÉATION DE L'UTILISATEUR APPLICATIF SÉCURISÉ ---
        app_user = "app_user"
        app_password = "UserSecurePass123!"
        
        existing_users = db.command("usersInfo")["users"]
        if not any(u["user"] == app_user for u in existing_users):
            print(f"🔑 Création de l'utilisateur applicatif '{app_user}'...")
            db.command("createUser", app_user, 
                       pwd=app_password, 
                       roles=[{"role": "readWrite", "db": "healthcare_db"}])
            print("🔑 Utilisateur créé avec succès.")
        else:
            print("🔑 L'utilisateur applicatif existe déjà.")
            
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
