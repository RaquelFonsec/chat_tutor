  Professor Tutor de Análise de Dados com FastAPI
  

Este projeto é uma API desenvolvida com FastAPI que serve como backend para um assistente inteligente focado em responder perguntas sobre Análise de Dados, no contexto do Bootcamp da SoulCode. A API integra-se com modelos de linguagem grandes (LLMs) como OpenRouter e Groq, utiliza um banco de dados MongoDB para persistir conversas e oferece sugestões de cursos.



## Funcionalidades Principais


- **Processamento de Perguntas**: Recebe perguntas de usuários e utiliza LLMs para gerar respostas contextuais.
- **Sugestão de Cursos**: Analisa a pergunta do usuário e sugere cursos relevantes da SoulCode.
- **Persistência de Conversas**: Salva o histórico de perguntas e respostas em um banco de dados MongoDB.
- **Verificação de Origem da Resposta**: Tenta identificar a fonte da informação (Banco de Dados, Documentação Oficial, LLM).
- **Endpoints**: Fornece endpoints para fazer perguntas, listar cursos e verificar a saúde da API.



## Estrutura do Projeto


├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configurações da aplicação, chaves de API, prompts
│   │   ├── db_config.py      # Configuração da conexão com MongoDB
│   │   └── llm_config.py       # Configuração dos LLMs e embeddings
│   ├── data/
│   │   └── cursos_soulcode.json # Dados dos cursos
│   ├── models/
│   │   ├── __init__.py
│   │   └── pydantic_models.py # Modelos Pydantic para validação de dados
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py           # Endpoints da API (perguntas, cursos)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversa_service.py # Lógica para salvar e consultar conversas
│   │   ├── curso_service.py    # Lógica para carregar e sugerir cursos
│   │   └── resposta_service.py # Lógica principal de processamento de perguntas
│   ├── __init__.py
│   └── main.py             # Arquivo principal da aplicação FastAPI
├── .env                    
├── .env.example            
├── requirements.txt        
├── todo.md               
└── README.md               
```



## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Acesso a um servidor MongoDB (local ou Atlas) - Opcional para rodar, mas necessário para persistência.
- Chaves de API para OpenRouter e/ou Groq (para funcionalidade completa do LLM).



## Configuração do Ambiente



1.  **Clone o repositório ou baixe os arquivos do projeto.**



2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate    # No Windows
    ```

3.  **Instale as dependências:**
    Navegue até o diretório raiz do projeto (onde `requirements.txt` está localizado) e execute:
    ```bash
    pip install -r requirements.txt
    ```


4.  **Configure as Variáveis de Ambiente:**
    Copie o arquivo `.env.example` para um novo arquivo chamado `.env` no diretório raiz do projeto:
    ```bash
    cp .env.example .env
    ```
    Edite o arquivo `.env` e preencha com suas chaves de API e detalhes de conexão do MongoDB:

    ```env
    OPENROUTER_API_KEY="SUA_CHAVE_API_OPENROUTER_AQUI"
    GROQ_API_KEY="SUA_CHAVE_API_GROQ_AQUI"



    # Se estiver usando MongoDB Atlas ou uma URI de conexão completa:
    MONGODB_API_KEY="mongodb+srv://USER:PASS@HOST/DBNAME?retryWrites=true&w=majority&appName=assistenteIA"



    # OU, se estiver configurando usuário, senha, host separadamente (para srv ou local):
    MONGODB_USER="SEU_USUARIO_MONGODB"
    MONGODB_PASSWORD="SUA_SENHA_MONGODB"
    MONGODB_HOST="SEU_HOST_MONGODB_COM_PORTA_SE_NECESSARIO" # Ex: cluster0.xyz.mongodb.net ou localhost:27017
    MONGODB_DB_NAME="assistenteIA"
    ```


    - Se `MONGODB_API_KEY` for fornecida, ela terá precedência.
    - Se `MONGODB_USER`, `MONGODB_PASSWORD`, e `MONGODB_HOST` forem fornecidos, uma URI `mongodb+srv://` será construída.
    - Se nenhuma credencial for fornecida, tentará conectar a `mongodb://localhost:27017/assistenteIA`.

## Como Executar a Aplicação


No diretório raiz do projeto, execute o servidor Uvicorn:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


- `--reload`: Faz o servidor reiniciar automaticamente após alterações no código (útil para desenvolvimento).
- `--host 0.0.0.0`: Torna a API acessível na rede local.
- `--port 8000`: Define a porta em que a API será executada.



Após a execução, a API estará disponível em `http://localhost:8000` (ou `http://SEU_IP_LOCAL:8000`).

## Como Usar a API


A API FastAPI gera automaticamente uma documentação interativa (Swagger UI) que pode ser acessada em:

`http://localhost:8000/docs`

Lá você pode visualizar todos os endpoints, seus parâmetros, modelos de dados e testá-los diretamente no navegador.



### Endpoints Principais


1.  **`POST /api/pergunta`**
    -   **Descrição**: Envia uma pergunta para o assistente de IA.
    -   **Corpo da Requisição** (JSON):
        ```json
        {
          "texto_pergunta": "O que é Pandas em Python?"
        }
        ```
    -   **Resposta Exemplo** (JSON):
        ```json
        {
          "pergunta_original": "O que é Pandas em Python?",
          "texto_resposta": "Pandas é uma biblioteca de software escrita para a linguagem de programação Python para manipulação e análise de dados. Em particular, oferece estruturas e operações de dados para manipular tabelas numéricas e séries temporais...\n\n🎓 **Sugestão de curso: [Nome do Curso Sugerido](http://link.curso.sugerido)**\n\n🔗 **Documentação Relacionada:**\n- https://pandas.pydata.org/docs/",
          "origem_resposta": "Nova Geração pelo LLM (ref: https://www.google.com/search?q=O+que+%C3%A9+Pandas+em+Python%3F)",
          "sugestao_curso": {
            "nome_curso": "Nome do Curso Sugerido",
            "link_curso": "http://link.curso.sugerido"
          },
          "links_documentacao": [
            "https://pandas.pydata.org/docs/"
          ]
        }
        ```

2.  **`GET /api/cursos`**
    -   **Descrição**: Lista todos os cursos disponíveis carregados a partir do arquivo `cursos_soulcode.json`.
    -   **Resposta Exemplo** (JSON):
        ```json
        [
          {
            "Curso": "Curso de Exemplo 1",
            "Link": "http://example.com/curso1",
            "Palavras_chave": "exemplo, curso, aprendizado"
          },
          {
            "Curso": "Curso de Exemplo 2",
            "Link": "http://example.com/curso2",
            "Palavras_chave": "outro, exemplo, tecnologia"
          }
        ]
        ```

3.  **`GET /health`**
    -   **Descrição**: Verifica o status da API e suas conexões (ex: MongoDB).
    -   **Resposta Exemplo** (JSON):
        ```json
        {
          "status": "ok",
          "message": "API está operacional",
          "mongodb_status": "conectado",
          "openrouter_key_loaded": true,
          "groq_key_loaded": true
        }
        ```

## Variáveis de Ambiente Detalhadas (`.env`)

-   `OPENROUTER_API_KEY`: Sua chave de API para OpenRouter.ai.
-   `GROQ_API_KEY`: Sua chave de API para GroqCloud.
-   `MONGODB_API_KEY`: URI de conexão completa para o MongoDB Atlas (ex: `mongodb+srv://...`). Se preenchida, tem prioridade sobre os campos abaixo.
-   `MONGODB_USER`: Nome de usuário para autenticação no MongoDB.
-   `MONGODB_PASSWORD`: Senha para autenticação no MongoDB.
-   `MONGODB_HOST`: Hostname (e porta, se não for a padrão) do servidor MongoDB. Para Atlas, é o host do cluster. Para local, pode ser `localhost:27017`.
-   `MONGODB_DB_NAME`: Nome do banco de dados a ser utilizado no MongoDB (padrão: `assistenteIA`).



## Considerações

-   A qualidade das respostas do LLM depende da qualidade dos prompts e do modelo LLM escolhido.
-   Certifique-se de que as dependências em `requirements.txt` estão atualizadas e compatíveis.


