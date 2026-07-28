import os
import time
from urllib.parse import quote_plus
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from dotenv import load_dotenv


def print_benchmark(title, explain_result):
    stats = explain_result.get("executionStats", {})
    print(f"\n--- {title} ---")
    print(f"⏱️ Temps d'exécution      : {stats.get('executionTimeMillis', 0)} ms")
    print(f"📄 Documents examinés    : {stats.get('totalDocsExamined', 0)}")
    print(f"✅ Documents retournés    : {stats.get('nReturned', 0)}")
    
    # Récupération du stage (COLLSCAN, IXSCAN, etc.)
    winning_stage = stats.get('executionStages', {}).get('stage', 'N/A')
    print(f"🔍 Type de scan utilisé   : {winning_stage}")


def get_explain_stats(db, collection_name, query):
    """
    Exécute la commande 'explain' compatible avec PyMongo 4+
    en mode 'executionStats'.
    """
    return db.command('explain', {
        'find': collection_name,
        'filter': query
    }, verbosity='executionStats')


def tester_indexes():
    print("🚀 Début du benchmark et du test d'indexation...")
    load_dotenv()

    # Récupération des variables d'environnement
    MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_db")

    APP_USER = quote_plus(os.getenv("APP_USER_USERNAME", "app_user"))
    APP_PASS = quote_plus(os.getenv("APP_USER_PASSWORD", "userpass"))

    # URI applicative
    uri_applicative = f"mongodb://{APP_USER}:{APP_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource={DB_NAME}"

    client = None
    try:
        # 1. Connexion à la base
        client = MongoClient(uri_applicative, serverSelectionTimeoutMS=3000)
        db = client[DB_NAME]
        collection = db['patients']

        # ==========================================
        # 0. SUPPRESSION DES INDEX EXISTANTS (Hors _id)
        # ==========================================
        collection.drop_indexes()
        print("🧹 Tous les index secondaires ont été supprimés pour le test AVANT.")

        # Vérification rapide de la présence de données
        total_docs = collection.count_documents({})
        if total_docs == 0:
            print("⚠️ Attention : La collection 'patients' est vide. Lancez 'migrate.py' d'abord.")
            return

        print(f"📊 Nombre de documents dans la collection : {total_docs}")

        # ==========================================
        # 1. TEST INDEX SIMPLE : Medical Condition
        # ==========================================
        query_simple = {"Medical Condition": "Cancer"}

        # AVANT Index
        exp_before = get_explain_stats(db, 'patients', query_simple)
        print_benchmark("1. Index Simple (AVANT)", exp_before)

        # CRÉATION INDEX SIMPLE
        collection.create_index([("Medical Condition", ASCENDING)], name="idx_medical_condition")

        # APRÈS Index
        exp_after = get_explain_stats(db, 'patients', query_simple)
        print_benchmark("1. Index Simple (APRÈS)", exp_after)

        # ==========================================
        # 2. TEST INDEX COMPOSÉ : Medical Condition + Date of Admission
        # ==========================================
        query_compound = {
            "Medical Condition": "Diabetes",
            "Date of Admission": {"$gte": "2023-01-01"}
        }

        # AVANT Index Composé
        exp_comp_before = get_explain_stats(db, 'patients', query_compound)
        print_benchmark("2. Index Composé (AVANT)", exp_comp_before)

        # CRÉATION INDEX COMPOSÉ
        collection.create_index([
            ("Medical Condition", ASCENDING),
            ("Date of Admission", DESCENDING)
        ], name="idx_condition_date")

        # APRÈS Index Composé
        exp_comp_after = get_explain_stats(db, 'patients', query_compound)
        print_benchmark("2. Index Composé (APRÈS)", exp_comp_after)

        # ==========================================
        # 3. TEST INDEX UNIQUE : Name (ou champ unique existant)
        # ==========================================
        query_unique = {"Name": "Bobby Jackson"}

        # AVANT Index
        exp_uniq_before = get_explain_stats(db, 'patients', query_unique)
        print_benchmark("3. Index recherche de nom (AVANT)", exp_uniq_before)

        # CRÉATION INDEX NOM
        collection.create_index([("Name", ASCENDING)], name="idx_patient_name")

        # APRÈS Index
        exp_uniq_after = get_explain_stats(db, 'patients', query_unique)
        print_benchmark("3. Index recherche de nom (APRÈS)", exp_uniq_after)

    except OperationFailure as e:
        print(f"❌ Erreur de droits/opération MongoDB : {e}")
        print("💡 Vérifiez que l'utilisateur a bien les droits 'readWrite' sur la base.")
    except ConnectionFailure:
        print("❌ Erreur : Impossible de joindre le serveur MongoDB.")
    except PyMongoError as e:
        print(f"⚠️ Erreur spécifique PyMongo : {e}")
    except Exception as e:
        print(f"❓ Une erreur inattendue est survenue : {e}")
    finally:
        if client:
            client.close()
            print("\n🔌 Connexion fermée.")

if __name__ == "__main__":
    tester_indexes()

