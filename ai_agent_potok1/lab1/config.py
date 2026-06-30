"""Подключение к LLM + Cost tracking (OpenRouter + LiteLLM)."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== LiteLLM Proxy ==========

def get_litellm_llm(model: str = "agent-llm"):
    """Через LiteLLM proxy."""
    return ChatOpenAI(
        model=model,
        api_key="sk-litellm-master-key-123",
        base_url="http://localhost:4000",
        temperature=0.1,
    )


# ========== Прямые подключения ==========

def get_airouter_llm(model: str = "deepseek/deepseek-v4-flash"):
    """AI Router напрямую."""
    key = os.getenv("AIROUTER_API_KEY")
    if not key:
        raise ValueError("AIROUTER_API_KEY не найден!")
    
    return ChatOpenAI(
        model=model,
        api_key=key,
        base_url="https://api.ai-router.app/v1",
        temperature=0.1,
    )


def get_openrouter_llm(model: str = "openai/gpt-4o-mini"):
    """OpenRouter напрямую."""
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY не найден!")
    
    return ChatOpenAI(
        model=model,
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
    )


# ========== Cost Tracking через OpenRouter ==========

def get_openrouter_credits():
    """Получает баланс и статистику с OpenRouter."""
    import requests
    
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return {"error": "OPENROUTER_API_KEY не найден"}
    
    try:
        # Баланс
        credits = requests.get(
            "https://openrouter.ai/api/v1/credits",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        
        # Использование
        usage = requests.get(
            "https://openrouter.ai/api/v1/usage",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        
        return {
            "credits": credits.json() if credits.status_code == 200 else {"error": credits.text},
            "usage": usage.json() if usage.status_code == 200 else {"error": usage.text},
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_openrouter_generation_stats():
    """Статистика по последним запросам."""
    import requests
    
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return {"error": "OPENROUTER_API_KEY не найден"}
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/generation",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


# ========== Cost Tracking через LiteLLM (fallback) ==========

def get_litellm_spend_logs():
    """Пробуем получить логи LiteLLM (без БД может не работать)."""
    import requests
    
    try:
        response = requests.get(
            "http://localhost:4000/spend/logs",
            headers={"Authorization": "Bearer sk-litellm-master-key-123"},
            timeout=5,
        )
        return response.json() if response.status_code == 200 else {"status": response.status_code, "note": "Без БД логи не хранятся"}
    except Exception as e:
        return {"error": str(e)}


# ========== Универсальный cost tracker ==========

def get_cost_report():
    """Общий отчёт по расходам (все провайдеры)."""
    report = {
        "openrouter": get_openrouter_credits(),
        "litellm_logs": get_litellm_spend_logs(),
    }
    return report


def print_cost_report():
    """Красивый вывод расходов."""
    print("\n" + "=" * 60)
    print("=== 💰 COST REPORT ===")
    print("=" * 60)
    
    report = get_cost_report()
    
    # OpenRouter
    or_data = report.get("openrouter", {})
    if "error" not in or_data:
        credits = or_data.get("credits", {})
        usage = or_data.get("usage", {})
        
        print("\n--- OpenRouter ---")
        if "data" in credits:
            print(f"Баланс: ${credits['data'].get('total_credits', 'N/A')}")
            print(f"Использовано: ${credits['data'].get('total_usage', 'N/A')}")
        if "data" in usage:
            print(f"Запросов: {len(usage['data'])}")
    else:
        print(f"\n--- OpenRouter: {or_data['error']} ---")
    
    # LiteLLM
    llm_data = report.get("litellm_logs", {})
    print(f"\n--- LiteLLM ---")
    print(f"Статус: {llm_data.get('note', llm_data.get('status', 'N/A'))}")
    
    print("\n" + "=" * 60)

# ========== Нативные провайдеры (если ключи есть) ==========

def get_deepseek_llm():
    """DeepSeek напрямую."""
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("DEEPSEEK_API_KEY не найден!")
    
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.1,
    )


def get_qwen_llm():
    """Qwen через DashScope."""
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        raise ValueError("DASHSCOPE_API_KEY не найден!")
    
    return ChatOpenAI(
        model="qwen-max",
        api_key=key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1,
    )


def get_kimi_llm():
    """Kimi (Moonshot AI)."""
    key = os.getenv("MOONSHOT_API_KEY")
    if not key:
        raise ValueError("MOONSHOT_API_KEY не найден!")
    
    return ChatOpenAI(
        model="kimi-latest",
        api_key=key,
        base_url="https://api.moonshot.cn/v1",
        temperature=0.1,
    )

# ========== Фабрика ==========

def get_llm(provider: str = "litellm"):
    """Фабрика LLM."""
    providers = {
        "litellm": get_litellm_llm,
        "airouter": get_airouter_llm,
        "openrouter": get_openrouter_llm,
        "deepseek": get_deepseek_llm,
        "qwen": get_qwen_llm,
        "kimi": get_kimi_llm,
    }
    
    if provider in providers:
        return providers[provider]()
    
    # Кастомные модели через префикс
    if provider.startswith("litellm:"):
        model = provider.replace("litellm:", "")
        return get_litellm_llm(model)
    
    if provider.startswith("airouter:"):
        model = provider.replace("airouter:", "")
        return get_airouter_llm(model)
    
    if provider.startswith("openrouter:"):
        model = provider.replace("openrouter:", "")
        return get_openrouter_llm(model)
    
    raise ValueError(f"Неизвестный провайдер: {provider}")
    