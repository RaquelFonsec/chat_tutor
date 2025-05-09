import hashlib
from datetime import datetime
from app.core.db_config import get_db_collection
from app.models.pydantic_models import ConversaDBModel
from app.core.config import settings
from pymongo.errors import ConnectionFailure, OperationFailure
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def gerar_hash_resposta(resposta: str) -> str:
    return hashlib.md5(resposta.encode()).hexdigest()

def salvar_conversa_service(pergunta: str, resposta: str, origem: str) -> bool:
    collection = get_db_collection()
    if not collection:
        print("❌ Coleção do MongoDB não disponível. Não foi possível salvar a conversa.")
        return False

    hash_resposta = gerar_hash_resposta(resposta)
    
    conversa = ConversaDBModel(
        pergunta=pergunta,
        resposta=resposta,
        hash_resposta=hash_resposta,
        origem=origem,
        data_hora=datetime.now()
    )
    
    try:
        collection.insert_one(conversa.dict())
        print("✅ Conversa salva com sucesso no MongoDB!")
        return True
    except ConnectionFailure:
        print("❌ Falha de conexão ao tentar salvar conversa no MongoDB.")
    except OperationFailure as e:
        print(f"❌ Falha na operação ao tentar salvar conversa no MongoDB: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao salvar conversa: {e}")
    return False

def consultar_resposta_banco_service(pergunta: str, threshold: float = 0.65) -> Optional[str]:
    collection = get_db_collection()
    if not collection:
        print("❌ Coleção do MongoDB não disponível. Não foi possível consultar o banco.")
        return None

    try:
        # Busca todas as conversas para cálculo de similaridade localmente
        # Para grandes volumes, considerar soluções de busca mais robustas (ex: Atlas Search)
        documentos = list(collection.find({}, {"pergunta": 1, "resposta": 1, "_id": 0}))
    except Exception as e:
        print(f"Erro ao buscar documentos no MongoDB: {e}")
        return None

    if not documentos:
        return None

    perguntas_banco = [doc["pergunta"] for doc in documentos]
    respostas_banco = [doc["resposta"] for doc in documentos]

    try:
        # Adiciona a pergunta atual à lista para vetorização
        textos_para_vetorizacao = [pergunta] + perguntas_banco
        vectorizer = TfidfVectorizer().fit_transform(textos_para_vetorizacao)
        
        # Calcula a similaridade entre a pergunta atual (primeiro vetor) e todas as perguntas do banco
        similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    except ValueError as e:
        print(f"Erro ao calcular similaridade TF-IDF (consultar_resposta_banco): {e}")
        return None # Retorna None se houver erro na vetorização

    if not similarities.size > 0:
        return None

    max_idx = similarities.argmax()
    if similarities[max_idx] >= threshold:
        print(f"Resposta similar encontrada no banco com similaridade {similarities[max_idx]:.2f}")
        return respostas_banco[max_idx]
    
    return None

