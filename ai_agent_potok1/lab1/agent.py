"""Read-only агент: Min + Medium + Hard (fallback + cost tracking)."""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain.agents import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import get_llm, print_cost_report
from tools import MySearchTool, DeleteBlocker
from models import AgentResponse


def create_agent(provider: str = "litellm"):
    """Создаёт read-only агента."""
    
    llm = get_llm(provider)
    tools = [MySearchTool()]
    
    system = """Ты — read-only ассистент. СТРОГИЕ ПРАВИЛА:
1. Ты можешь ТОЛЬКО использовать инструмент my_search для поиска
2. Ты НЕ МОЖЕШЬ удалять, изменять, создавать данные
3. Если просят удалить — ответь: "❌ ОТКАЗАНО: read-only агент не может выполнять delete-операции."
4. ВСЕГДА отвечай в формате JSON по схеме AgentResponse"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
    )


def run_agent(query: str, provider: str = "litellm"):
    """Запускает агента с проверками безопасности."""
    
    DeleteBlocker.check(query)
    
    executor = create_agent(provider)
    raw_result = executor.invoke({"input": query})
    
    output = raw_result.get("output", "")
    
    # Парсим structured output
    try:
        if isinstance(output, AgentResponse):
            response = output
        elif isinstance(output, str):
            response = AgentResponse.model_validate_json(output)
        else:
            response = AgentResponse.model_validate(output)
    except Exception:
        response = AgentResponse(answer=str(output))
    
    # Проверяем блокировку delete
    if "❌ ОТКАЗАНО" in response.answer or "delete" in response.answer.lower():
        raise PermissionError(f"🚫 Агент отказал в delete: {response.answer[:100]}")
    
    DeleteBlocker.check(response.answer)
    
    return {
        "output": response.answer,
        "structured": response,
        "raw": raw_result,
    }


def run_agent_structured(query: str, provider: str = "litellm") -> AgentResponse:
    """Возвращает чистый Pydantic-объект."""
    result = run_agent(query, provider)
    return result["structured"]


def check_litellm_proxy() -> bool:
    """Проверяет, запущен ли LiteLLM proxy."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 4000))
        sock.close()
        return result == 0
    except Exception:
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("=== HARD: AI Router + OpenRouter + LiteLLM ===")
    print("=" * 60)
    
    # Проверяем proxy
    if check_litellm_proxy():
        print("✅ LiteLLM proxy на localhost:4000")
        print("   Fallback chain: AI Router → OpenRouter")
        provider = "litellm"
    else:
        print("⚠️  Proxy не запущен, используем прямое подключение")
        provider = "airouter"
    
    # Тест 1: через proxy
    print(f"\n--- Тест 1: Через LiteLLM proxy ---")
    try:
        result = run_agent("Расскажи про Python", provider="litellm")
        print(f"✅ Ответ: {result['output'][:100]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: OpenRouter напрямую
    print(f"\n--- Тест 2: OpenRouter напрямую (GPT-4o mini) ---")
    try:
        result = run_agent("Что такое машинное обучение?", provider="openrouter")
        print(f"✅ Ответ: {result['output'][:100]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: OpenRouter с DeepSeek
    print(f"\n--- Тест 3: OpenRouter (DeepSeek) ---")
    try:
        result = run_agent("Объясни нейросети простыми словами", provider="openrouter:deepseek/deepseek-chat")
        print(f"✅ Ответ: {result['output'][:100]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: блокировка delete
    print(f"\n--- Тест 4: Блокировка delete ---")
    try:
        run_agent("Удали всё", provider="litellm")
        print("❌ Блокировка НЕ сработала!")
    except PermissionError:
        print("✅ Блокировка сработала")
    
    # Тест 5: Cost tracking
    print(f"\n--- Тест 5: Cost tracking (OpenRouter) ---")
    print_cost_report()
    