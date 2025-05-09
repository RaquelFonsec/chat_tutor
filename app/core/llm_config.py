from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from app.core.config import settings
import os

# Configurar chaves de API para Langchain
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["OPENAI_API_BASE"] = settings.OPENAI_API_BASE
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

def get_openrouter_llm():
    return ChatOpenAI(
        model_name="deepseek/deepseek-r1:free", # ou outro modelo disponível
        temperature=0.2,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE
    )

def get_groq_llm():
    return ChatGroq(
        model_name="llama-3.3-70b-versatile", # ou llama3-8b-8192 ou outro
        temperature=0.2,
        groq_api_key=settings.GROQ_API_KEY
    )

def get_embeddings_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_conversation_chain(llm_preference="openrouter"):
    memoria = ConversationBufferMemory(
        memory_key="history",
        return_messages=True
    )

    # O template original era """{history}\nAluno: {input}\nResposta TESTE:"""
    # Ajustado para um formato mais genérico, o "Resposta TESTE:" pode ser desnecessário
    # ou o LLM pode ser instruído a não usar esse prefixo na resposta final.
    # O system_prompt já está sendo injetado no input do chain mais adiante.
    template_str = """{history}\nHumano: {input}\nAssistente:"""
    template = PromptTemplate.from_template(template_str)

    llm = None
    if llm_preference == "openrouter":
        try:
            llm = get_openrouter_llm()
            print("\n✅ LLM via OPENROUTER selecionado.")
        except Exception as e_openrouter:
            print(f"\n⚠️ Erro ao inicializar OpenRouter LLM: {e_openrouter}. Tentando Groq...")
            try:
                llm = get_groq_llm()
                print("\n✅ LLM via GROQ selecionado como fallback.")
            except Exception as e_groq:
                print(f"\n❌ Erro ao inicializar Groq LLM: {e_groq}. Nenhum LLM disponível.")
                raise Exception("Nenhum LLM pôde ser inicializado.")
    elif llm_preference == "groq":
        try:
            llm = get_groq_llm()
            print("\n✅ LLM via GROQ selecionado.")
        except Exception as e_groq:
            print(f"\n⚠️ Erro ao inicializar Groq LLM: {e_groq}. Tentando OpenRouter...")
            try:
                llm = get_openrouter_llm()
                print("\n✅ LLM via OPENROUTER selecionado como fallback.")
            except Exception as e_openrouter:
                print(f"\n❌ Erro ao inicializar OpenRouter LLM: {e_openrouter}. Nenhum LLM disponível.")
                raise Exception("Nenhum LLM pôde ser inicializado.")
    else:
        raise ValueError("Preferência de LLM inválida. Escolha 'openrouter' ou 'groq'.")

    if llm is None:
        raise Exception("Falha ao carregar qualquer LLM.")

    chat_chain = ConversationChain(
        llm=llm,
        memory=memoria,
        prompt=template,
        verbose=False # Defina como True para debugging detalhado das chamadas do LLM
    )
    return chat_chain

# Para testes rápidos:
if __name__ == "__main__":
    try:
        # Teste OpenRouter
        print("Testando OpenRouter LLM...")
        #chain_or = get_conversation_chain(llm_preference="openrouter")
        #response_or = chain_or.run("Olá")
        #print(f"Resposta OpenRouter: {response_or}")
        
        # Teste Groq
        print("\nTestando Groq LLM...")
        #chain_gq = get_conversation_chain(llm_preference="groq")
        #response_gq = chain_gq.run("Olá")
        #print(f"Resposta Groq: {response_gq}")

        # Teste Embeddings
        print("\nTestando Embeddings Model...")
        #embeddings = get_embeddings_model()
        #query_result = embeddings.embed_query("Teste de embedding")
        #print(f"Embedding gerado (primeiros 10 valores): {query_result[:10]}")
        print("Configurações de LLM e Embeddings carregadas.")

    except Exception as e:
        print(f"Erro durante o teste de llm_config: {e}")