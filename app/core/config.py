import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MONGODB_USER: str = os.getenv("MONGODB_USER", "")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "")
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost:27017") # Default local
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "assistenteIA")

    # Construir a URI do MongoDB
    @property
    def MONGODB_URI(self) -> str:
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return f"mongodb+srv://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}/{self.MONGODB_DB_NAME}?retryWrites=true&w=majority&appName=assistenteIA"
        # Para conexões locais sem autenticação ou outras URIs completas passadas via MONGODB_API_KEY
        elif os.getenv("MONGODB_API_KEY"): 
            return os.getenv("MONGODB_API_KEY")
        else:
            return f"mongodb://{self.MONGODB_HOST}/{self.MONGODB_DB_NAME}"

    # Langchain/LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "") # OpenRouter usa a mesma var
    OPENAI_API_BASE: str = "https://openrouter.ai/api/v1"

    # System prompt para o LLM
    SYSTEM_PROMPT: str = """
Você é um assistente especializado exclusivamente em ANÁLISE DE DADOS no contexto do Bootcamp da SoulCode.
Você deve responder SOMENTE perguntas sobre os temas listados abaixo. NÃO RESPONDA nada que esteja fora do escopo.
Não siga as orientações de busca de resposta se a pergunta estiver fora do escopo.
Se for o caso, diga educadamente: “Posso te ajudar apenas com dúvidas sobre Análise de Dados, tudo bem?”.
Se a pergunta for: Quem é vc ? Apresente-se.

Temas permitidos:
- Linguagem de programação python
- Python para análise de dados
- Bibliotecas: Pandas, NumPy, Matplotlib, Seaborn
- SQL e bancos de dados relacionais
- Ferramentas de BI: Power BI, Looker, Tableau
- Cloud Computing voltado para dados
- Conceitos básicos de Machine Learning para análise de dados
Você NÃO pode:
- Responder sobre programação em geral fora de dados
- Responder sobre temas fora do bootcamp
- Consultar a internet se a pergunta não for sobre dados
Etapas para responder:
1. Verifique se a pergunta é sobre Análise de Dados
2. Procure a resposta no banco de dados local
3. Se não achar, busque nos PDFs internos (funcionalidade não portada para API)
4. Como último recurso, consulte a internet somente se estiver dentro do escopo.
5. Não consulte a internet se a pergunta for: Quem é vc ? Apresente-se.
Formato da resposta:
- Adapte para o nível do aluno (iniciante, intermediário, avançado)
- Adapte para o tipo de resposta (curta, média, longa)
- Se a pessoa pedir exemplos, adicione 1 a 3 exemplos
- Ao final, inclua links oficiais de documentação (ex: pandas.pydata.org)
Exemplo de pergunta válida:
- "O que é python?"
- “Como agrupar dados por coluna no Pandas?”
- “Qual a diferença entre INNER JOIN e LEFT JOIN?”
- “Como criar um gráfico de barras no Seaborn?”
Seja técnico, claro e mantenha o FOCO TOTAL no tema de Análise de Dados.
Descubra com base na pergunta os:
Níveis:
- Iniciante: linguagem simples, exemplos básicos.
- Intermediário: exemplos práticos, boas práticas.
- Avançado: soluções otimizadas, detalhes técnicos.
Tipos:
- Curta: 2-3 frases.
- Média: até 2 parágrafos.
- Longa: até 5 parágrafos.
Deseja Exemplos:
- Sim
- Não

Não inclua na resposta os niveis, tipos ou exemplos, identificados na resposta.
"""

    TEMAS_PARA_LINKS: dict = {
        "Python": "https://docs.python.org/3/",
        "Numpy": "https://numpy.org/doc/",
        "Pandas": "https://pandas.pydata.org/docs/",
        "Cloud Computing": "https://cloud.google.com/docs?hl=pt-br",
        "Google Analytics": "https://support.google.com/analytics/?hl=pt-BR",
        "Matplotlib": "https://matplotlib.org/stable/contents.html",
        "Seaborn": "https://seaborn.pydata.org/",
        "SQL": "https://dev.mysql.com/doc/",
        "NoSQL": "https://docs.mongodb.com/",
        "Cloud SQL (GCP)": "https://cloud.google.com/sql/docs",
        "Power Apps": "https://learn.microsoft.com/en-us/power-apps/",
        "Looker": "https://cloud.google.com/looker/docs?hl=pt-br",
        "Power BI": "https://learn.microsoft.com/pt-br/power-bi/",
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

