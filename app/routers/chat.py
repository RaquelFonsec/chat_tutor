from fastapi import APIRouter, HTTPException, Depends
from app.models.pydantic_models import PerguntaInputModel, RespostaOutputModel, CursoModel
from app.services.resposta_service import processar_pergunta_service
from app.services.curso_service import get_todos_cursos, carregar_cursos_json
from typing import List

router = APIRouter()

@router.post("/pergunta", response_model=RespostaOutputModel)
async def perguntar_ao_assistente(pergunta_input: PerguntaInputModel):
    """
    Recebe uma pergunta do usuário e retorna a resposta processada pelo assistente de IA.
    A resposta inclui o texto, a origem da informação, sugestão de curso e links de documentação.
    """
    try:
        # Garante que os cursos sejam carregados antes de processar a pergunta, 
        # pois o processar_pergunta_service pode chamar o sugerir_curso_service
        carregar_cursos_json() # Assegura que os dados dos cursos estão na memória
        resposta = processar_pergunta_service(pergunta_input)
        return resposta
    except Exception as e:
        # Logar o erro e retornar uma HTTP Exception
        print(f"Erro crítico no endpoint /pergunta: {e}") # Idealmente, usar um logger mais robusto
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno ao processar sua pergunta: {str(e)}")

@router.get("/cursos", response_model=List[CursoModel])
async def listar_cursos():
    """
    Retorna uma lista de todos os cursos disponíveis no sistema.
    """
    try:
        cursos = get_todos_cursos()
        if not cursos:
            # Isso pode acontecer se o arquivo JSON não for encontrado ou estiver vazio
            raise HTTPException(status_code=404, detail="Nenhum curso encontrado ou arquivo de cursos indisponível.")
        return cursos
    except Exception as e:
        print(f"Erro no endpoint /cursos: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno ao buscar os cursos: {str(e)}")

# Adicionar outros endpoints conforme necessário, por exemplo, para status da API, etc.

