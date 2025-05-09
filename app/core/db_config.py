from pymongo import MongoClient
from app.core.config import settings

client = None
db = None
conversas_collection = None

def connect_to_mongo():
    global client, db, conversas_collection
    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DB_NAME]
        conversas_collection = db["conversas"]
        print("✅ Conectado ao MongoDB com sucesso!")
        # Test connection
        client.admin.command('ping')
        print("Ping no MongoDB bem-sucedido!")
    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")
        # Definir para None se a conexão falhar para evitar erros posteriores
        client = None
        db = None
        conversas_collection = None

def get_db_collection():
    if conversas_collection is None:
        # Tenta reconectar se a coleção não estiver disponível
        print("Tentando reconectar ao MongoDB...")
        connect_to_mongo()
    return conversas_collection

# Chamada inicial para conectar quando este módulo é carregado
# connect_to_mongo() # Removido para conectar explicitamente no startup da app FastAPI
