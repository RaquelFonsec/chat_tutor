import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.pydantic_models import CursoModel, CursoSugestaoModel
from app.core.config import settings
import os

# Caminho para o arquivo JSON de cursos
# Ajuste o caminho se o seu arquivo estiver em um local diferente dentro da estrutura do projeto
CURSOS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cursos_soulcode.json")

_cursos_soulcode_data: List[CursoModel] = []

def carregar_cursos_json(path_json: str = CURSOS_JSON_PATH) -> List[CursoModel]:
    global _cursos_soulcode_data
    if not _cursos_soulcode_data: # Carregar apenas uma vez
        try:
            with open(path_json, "r", encoding="utf-8") as f:
                cursos_raw = json.load(f)
                _cursos_soulcode_data = [CursoModel(**data) for data in cursos_raw]
                print(f"✅ {len(_cursos_soulcode_data)} cursos carregados de {path_json}")
        except FileNotFoundError:
            print(f"❌ Arquivo de cursos não encontrado em {path_json}. Nenhuma sugestão de curso estará disponível.")
            _cursos_soulcode_data = []
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar o JSON de cursos em {path_json}.")
            _cursos_soulcode_data = []
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar cursos: {e}")
            _cursos_soulcode_data = []
    return _cursos_soulcode_data

def get_todos_cursos() -> List[CursoModel]:
    return carregar_cursos_json() # Garante que os cursos sejam carregados se ainda não foram

def sugerir_curso_service(pergunta: str) -> Optional[CursoSugestaoModel]:
    cursos_data = get_todos_cursos()
    if not cursos_data:
        return None

    pergunta_lower = pergunta.lower().strip()
    
    cursos_nomes = [curso.Curso for curso in cursos_data]
    palavras_chave = [curso.Palavras_chave for curso in cursos_data]

    textos_para_vetorizacao = palavras_chave + [pergunta_lower]
    
    try:
        vectorizer = TfidfVectorizer().fit_transform(textos_para_vetorizacao)
        # Similaridade entre a pergunta (último item) e todas as palavras-chave dos cursos
        cosine_similarities = cosine_similarity(vectorizer[-1], vectorizer[:-1]).flatten()
    except ValueError as e:
        # Pode ocorrer se todos os documentos estiverem vazios ou se a pergunta for vazia após o processamento
        print(f"Erro ao calcular similaridade TF-IDF: {e}. Isso pode acontecer se a pergunta ou palavras-chave forem vazias.")
        return CursoSugestaoModel(
            nome_curso="Nenhum curso diretamente relacionado encontrado",
            link_curso="https://soulcodeacademy.org/passaporte"
        ) # Retorno padrão

    idx_max_similaridade = np.argmax(cosine_similarities)
    
    # Define um threshold de similaridade para considerar uma sugestão válida
    # O valor 0.3 foi usado no script original.
    SIMILARITY_THRESHOLD = 0.3 

    if cosine_similarities[idx_max_similaridade] >= SIMILARITY_THRESHOLD:
        curso_sugerido = cursos_data[idx_max_similaridade]
        return CursoSugestaoModel(
            nome_curso=curso_sugerido.Curso,
            link_curso=curso_sugerido.Link
        )
    else:
        # Se nenhuma sugestão atingir o threshold, pode-se retornar uma mensagem padrão
        # ou um link geral para explorar cursos.
        return CursoSugestaoModel(
            nome_curso="Nenhum curso diretamente relacionado encontrado. Explore o Passaporte SoulCode!",
            link_curso="https://soulcodeacademy.org/passaporte"
        )

# Para carregar os cursos quando o módulo é importado pela primeira vez
# carregar_cursos_json()

