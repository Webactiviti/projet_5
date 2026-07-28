import time
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError , OperationFailure
import os
from dotenv import load_dotenv

def tester_connexion_applicative():
    print("🔑 Tentative de connexion avec l'utilisateur applicatif 'app_user'...")
    # Charge les variables depuis le fichier .env s'il existe
    load_dotenv()

    # Récupération des variables d'environnement
    MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_db")

    APP_USER = os.getenv("APP_USER_USERNAME", "app_user")
    APP_PASS = os.getenv("APP_USER_PASSWORD", "userpass")
    

    
    # URI applicative
    uri_applicative = f"mongodb://{APP_USER}:{APP_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource={DB_NAME}"
    try:
        # Connexion ciblée sur 'healthcare_db'
        client = MongoClient(uri_applicative, serverSelectionTimeoutMS=2000)
        db = client[DB_NAME]
        collection = db['patients']
        
        # 1. On teste la lecture (récupérer 3 patients)
        print("🔎 Lecture des 3 premiers patients dans la base...")
        patients = list(collection.find().limit(3))
        
        if len(patients) == 0:
            print("⚠️ Connexion réussie, mais la collection 'patients' semble vide.")
        else:
            print("✅ Lecture réussie ! Voici un aperçu :")
            df = pd.DataFrame(patients)
            # On affiche proprement les colonnes principales avec Pandas
            print(df[['Name', 'Age', 'Gender', 'Medical Condition']].to_string(index=False))
            
        # 2. Test de sécurité (Vérification de la restriction des droits)
        # On essaie d'accéder à une autre base (ex: 'admin') pour vérifier que l'accès est bien refusé
        print("\n🛡️ Test de sécurité : tentative d'accès à la base système 'admin'...")
        client['admin'].command("usersInfo")
        print("❌ Alerte : L'utilisateur a pu accéder aux infos admin ! (Problème de droits)")
        
    except OperationFailure as e:
        # C'est l'erreur attendue pour le point 2, ce qui prouve que la sécurité fonctionne !
        if "not authorized" in str(e) or "requires authentication" in str(e):
            print("✅ Succès du test de sécurité ! L'accès aux bases système a été refusé (droits restreints conformes).")
        else:
            print(f"⚠️ Erreur d'opération inattendue : {e}")
            
    except ConnectionFailure:
        print("❌ Erreur : Impossible de joindre le serveur MongoDB.")
    except Exception as e:
        print(f"❓ Une autre erreur est survenue : {e}")
    finally:
        client.close()

if __name__ == "__main__":
    tester_connexion_applicative()
