from app.core.config import settings
from app.core.llm_config import get_conversation_chain
from app.services.conversa_service import consultar_resposta_banco_service, salvar_conversa_service
from app.services.curso_service import sugerir_curso_service
from app.models.pydantic_models import RespostaOutputModel, CursoSugestaoModel, PerguntaInputModel
import urllib.parse
import re
import hashlib
from app.core.db_config import get_db_collection # Para verificar hash no BD

# Funções adaptadas do script original

def identificar_tema_link(pergunta: str) -> Optional[str]:
    for tema, link in settings.TEMAS_PARA_LINKS.items():
        if tema.lower() in pergunta.lower():
            return link
    return None

def verificar_conhecimento_interno_llm(pergunta: str, resposta: str, chat_chain) -> bool:
    # Esta função é complexa de replicar 100% sem o LLM exato e contexto do script original.
    # No script original, ele usa o LLM para perguntar a si mesmo se a resposta é de conhecimento interno.
    # Para uma API, isso pode ser simplificado ou assumir que respostas do LLM sem consulta a BD/Docs são "conhecimento interno".
    # Por ora, vamos simular uma lógica mais simples ou pular essa verificação específica via LLM.
    # No script original: 
    # prompt_verificacao = f"""Esta resposta é do seu conhecimento interno? Responda APENAS com SIM ou NÃO:\nPergunta: {pergunta}\nResposta: {resposta}"""
    # verificacao = openrouter_llm.generate(prompt_verificacao).text.strip()
    # if verificacao.upper() == "SIM": return True
    # return False
    # Como alternativa, podemos verificar se a resposta está no buffer de memória recente do chat_chain
    if chat_chain and chat_chain.memory:
        buffer_str = str(chat_chain.memory.buffer_as_str) # ou buffer_as_messages
        if resposta in buffer_str: # Simplificação, pode não ser precisa
            return True
    return False # Defaulting to false if not found in recent memory or no reliable check

def verificar_origem_resposta_service(pergunta: str, resposta_bruta: str, chat_chain) -> str:
    print(f'\nVerificando origem da resposta para: {pergunta}')
    
    # 1. Verificar na memória de contexto do chat_chain (se aplicável e implementado no chain)
    if chat_chain and chat_chain.memory:
        # A memória do ConversationBufferMemory guarda o histórico.
        # Se a resposta exata estiver lá, pode ser considerada da memória.
        # Esta é uma verificação simplificada.
        if resposta_bruta in str(chat_chain.memory.buffer): # Convertendo buffer para string para busca
            origem = "Memória de Contexto da Conversa Atual"
            print(f'Detectado: {origem}')
            return origem

    # 2. Verificar no Banco de Dados (MongoDB) por hash ou regex (similar ao script original)
    collection = get_db_collection()
    if collection:
        hash_r = hashlib.md5(resposta_bruta.encode()).hexdigest()
        # Regex para buscar uma porção inicial da resposta, caso o hash não bata por pequenas variações
        resposta_regex_escaped = re.escape(resposta_bruta[:50]) 
        
        # Tenta encontrar por hash OU por uma parte da resposta (regex)
        # Adicionar filtro de persona/usuário se implementado no futuro
        resultado_db = collection.find_one({
            "$or": [
                {"hash_resposta": hash_r},
                {"resposta": {"$regex": resposta_regex_escaped, "$options": "i"}}
            ]
        })
        if resultado_db:
            origem_db = resultado_db.get('origem', 'Origem Desconhecida no BD')
            origem = f"Fonte Primária - Banco de Dados ({origem_db})"
            print(f'Detectado: {origem}')
            return origem

    # 3. Verificar se é sobre um tema com documentação oficial mapeada
    link_doc = identificar_tema_link(pergunta)
    if link_doc:
        origem = f"Fonte Secundária - Documentação Oficial ({link_doc})"
        print(f'Detectado: {origem}')
        return origem

    # 4. Tentar verificar se é conhecimento interno do LLM (heurística)
    # Esta parte é mais complexa de replicar fielmente sem chamar o LLM para se auto-avaliar.
    # A função `verificar_conhecimento_interno_llm` é uma tentativa.
    # if verificar_conhecimento_interno_llm(pergunta, resposta_bruta, chat_chain):
    #     origem = "Conhecimento Interno do LLM"
    #     print(f'Detectado: {origem}')
    #     return origem
    # Por ora, se não veio do BD ou Docs, e é uma resposta do LLM, vamos classificar como "Nova Geração pelo LLM"
    # ou "Conhecimento Interno do LLM" se a heurística acima for mais robusta.

    # 5. Se nenhuma das anteriores, assume-se que foi gerada pelo LLM (potencialmente com consulta web se o LLM tiver essa capacidade)
    # ou é uma nova geração baseada no prompt.
    # O script original adicionava um link de pesquisa Google como "Fonte Terciária".
    # url_pesquisa = f"https://www.google.com/search?q={urllib.parse.quote(pergunta)}"
    # origem = f"Fonte Terciária - Nova Geração pelo LLM (ref: {url_pesquisa})"
    # Simplificando para a API:
    origem = "Nova Geração pelo LLM"
    print(f'Detectado: {origem} (ou conhecimento interno não capturado pelas heurísticas anteriores)')
    return origem

def processar_pergunta_service(pergunta_input: PerguntaInputModel) -> RespostaOutputModel:
    pergunta_texto = pergunta_input.texto_pergunta.strip()
    
    if not pergunta_texto:
        # Comportamento do script original para pergunta vazia
        pergunta_texto = "Quem é vc ? Apresente-se."

    # 0. Tentar consultar resposta no banco antes de chamar o LLM
    resposta_do_banco = consultar_resposta_banco_service(pergunta_texto)
    sugestao_curso_obj = sugerir_curso_service(pergunta_texto)
    links_doc = []
    link_tema = identificar_tema_link(pergunta_texto)
    if link_tema:
        links_doc.append(link_tema)

    if resposta_do_banco:
        print("Resposta encontrada diretamente no banco de dados.")
        origem_final = "Fonte Primária - Banco de Dados (Consulta Direta por Similaridade)"
        # Adicionar sugestão de curso e links de documentação se aplicável
        resposta_final_formatada = f"{resposta_do_banco}"
        if sugestao_curso_obj:
             resposta_final_formatada += f"\n\n🎓 **Sugestão de curso: [{sugestao_curso_obj.nome_curso}]({sugestao_curso_obj.link_curso})**"
        if links_doc:
            resposta_final_formatada += "\n\n🔗 **Documentação Relacionada:**"
            for link in links_doc:
                resposta_final_formatada += f"\n- {link}"
        
        # Salvar a "nova" pergunta com a resposta do banco para fins de log/frequência, se desejado.
        # salvar_conversa_service(pergunta_texto, resposta_do_banco, origem_final) # Opcional, pois já está no banco
        
        return RespostaOutputModel(
            pergunta_original=pergunta_texto,
            texto_resposta=resposta_final_formatada,
            origem_resposta=origem_final,
            sugestao_curso=sugestao_curso_obj,
            links_documentacao=links_doc
        )

    # 1. Preparar o LLM e o prompt
    # Tenta OpenRouter primeiro, fallback para Groq se configurado no llm_config
    try:
        chat_chain = get_conversation_chain(llm_preference="openrouter") 
    except Exception as e:
        print(f"Falha ao obter chat_chain: {e}")
        # Tratar erro de LLM não disponível
        return RespostaOutputModel(
            pergunta_original=pergunta_texto,
            texto_resposta="Desculpe, o serviço de IA está temporariamente indisponível.",
            origem_resposta="Erro Interno - LLM Inacessível",
            sugestao_curso=sugestao_curso_obj, # Ainda pode sugerir curso
            links_documentacao=links_doc
        )

    # O system_prompt é parte da configuração do settings e usado no template do ConversationChain
    # ou pode ser injetado aqui se o template for mais simples.
    # No script original, o system_prompt era concatenado com a pergunta.
    # A ConversationChain com PromptTemplate já lida com a formatação do histórico e input.
    prompt_para_llm = f"{settings.SYSTEM_PROMPT}\n\nAluno: {pergunta_texto}\nAssistente:"
    # A label "Aluno:" e "Assistente:" ajuda o LLM a entender o papel.
    # O template da chain é "{history}\nHumano: {input}\nAssistente:"
    # Então o input para chain.run deve ser apenas a pergunta do usuário, 
    # e o system_prompt já está no template ou no llm.
    # Ajuste: O system_prompt deve ser parte do contexto inicial, não repetido a cada input se a memória já o contém.
    # Para a primeira mensagem ou se a memória não for persistente entre chamadas de API (o que é o caso aqui por padrão)
    # é bom incluir o system prompt.

    # Se a ConversationChain já tem um template que inclui o system_prompt, 
    # então o input para `run` seria apenas `pergunta_texto`.
    # Vamos assumir que o `get_conversation_chain` e seu `PromptTemplate` não incluem o `SYSTEM_PROMPT` diretamente,
    # então o concatenamos aqui como parte do `input`.
    # Revisão: O template é "{history}\nHumano: {input}\nAssistente:". 
    # O `SYSTEM_PROMPT` deve ser a primeira mensagem do `history` ou uma instrução para o LLM.
    # Para ConversationChain, o `system_message` pode ser setado na memória ou no LLM.
    # Se não, a forma mais simples é prefixar o input.

    # Se a memória for nova a cada chamada (típico de API stateless):
    if not chat_chain.memory.buffer: # Se a memória está vazia
        # Adiciona o system prompt como uma mensagem inicial do sistema ou do AI.
        # Isso não é padrão para ConversationBufferMemory, que espera tuplas (humano, ia).
        # Uma forma é passar o system_prompt como parte do primeiro input do usuário.
        input_llm = f"{settings.SYSTEM_PROMPT}\n\nPergunta específica: {pergunta_texto}"
    else:
        input_llm = pergunta_texto

    print(f"Enviando para LLM: {input_llm[:200]}...") # Log do input
    resposta_bruta_llm = chat_chain.run(input_llm)
    print(f"Resposta bruta do LLM: {resposta_bruta_llm[:200]}...")

    # 2. Verificar a origem da resposta do LLM
    origem_resposta_llm = verificar_origem_resposta_service(pergunta_texto, resposta_bruta_llm, chat_chain)

    # 3. Formatar a resposta final, adicionando sugestão de curso e links
    resposta_final_formatada = f"{resposta_bruta_llm}"
    
    if sugestao_curso_obj:
        resposta_final_formatada += f"\n\n🎓 **Sugestão de curso: [{sugestao_curso_obj.nome_curso}]({sugestao_curso_obj.link_curso})**"
    
    # Adicionar links de documentação se a origem não for já de documentação
    if links_doc and "Documentação Oficial" not in origem_resposta_llm:
        resposta_final_formatada += "\n\n🔗 **Documentação Relacionada:**"
        for link in links_doc:
            resposta_final_formatada += f"\n- {link}"
    elif "Documentação Oficial" in origem_resposta_llm: # Se a origem já é doc, o link já está lá
        pass 

    # Adicionar link de pesquisa genérico se a origem for "Nova Geração pelo LLM"
    if "Nova Geração pelo LLM" in origem_resposta_llm:
        url_pesquisa = f"https://www.google.com/search?q={urllib.parse.quote(pergunta_texto)}"
        resposta_final_formatada += f"\n\n🔗 **Para mais informações, consulte: {url_pesquisa}**"

    # 4. Salvar a conversa no MongoDB
    salvar_conversa_service(pergunta_texto, resposta_final_formatada, origem_resposta_llm)

    return RespostaOutputModel(
        pergunta_original=pergunta_texto,
        texto_resposta=resposta_final_formatada,
        origem_resposta=origem_resposta_llm,
        sugestao_curso=sugestao_curso_obj,
        links_documentacao=links_doc
    )

