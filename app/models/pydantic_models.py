from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PerguntaInputModel(BaseModel):
    texto_pergunta: str = Field(..., example="O que é Python?")

class CursoSugestaoModel(BaseModel):
    nome_curso: str
    link_curso: str

class RespostaOutputModel(BaseModel):
    pergunta_original: str
    texto_resposta: str
    origem_resposta: str
    sugestao_curso: Optional[CursoSugestaoModel] = None
    links_documentacao: Optional[List[str]] = None # Lista de URLs

class ConversaDBModel(BaseModel):
    #usuario: str = Field(default="ALUNO_API") # Ou pode ser obtido de um token JWT no futuro
    pergunta: str
    resposta: str
    hash_resposta: str
    origem: str
    data_hora: datetime = Field(default_factory=datetime.now)

class CursoModel(BaseModel):
    Curso: str
    Link: str
    Palavras_chave: str = Field(alias="Palavras-chave")
