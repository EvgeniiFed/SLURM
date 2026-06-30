"""Тесты OpenRouter — дополнительный провайдер."""

import pytest
from agent import run_agent, run_agent_structured
from config import get_openrouter_llm
from models import AgentResponse


def test_openrouter_direct_gpt4o_mini():
    """OpenRouter напрямую с GPT-4o mini."""
    try:
        result = run_agent("Тест OpenRouter", provider="openrouter")
        assert "structured" in result
        assert isinstance(result["structured"], AgentResponse)
        assert len(result["output"]) > 0
    except ValueError as e:
        if "OPENROUTER_API_KEY" in str(e):
            pytest.skip("Нет OPENROUTER_API_KEY")
        raise


def test_openrouter_deepseek():
    """OpenRouter с DeepSeek моделью."""
    try:
        result = run_agent(
            "Тест DeepSeek через OpenRouter",
            provider="openrouter:deepseek/deepseek-chat"
        )
        assert isinstance(result["structured"], AgentResponse)
    except ValueError as e:
        if "OPENROUTER_API_KEY" in str(e):
            pytest.skip("Нет OPENROUTER_API_KEY")
        raise


def test_openrouter_llm_creation():
    """Создание LLM через OpenRouter."""
    try:
        llm = get_openrouter_llm()
        assert llm is not None
    except ValueError as e:
        if "OPENROUTER_API_KEY" in str(e):
            pytest.skip("Нет OPENROUTER_API_KEY")
        raise


def test_all_providers_structured():
    """Structured output работает со всеми провайдерами."""
    providers = ["litellm", "airouter", "openrouter"]
    
    for provider in providers:
        try:
            response = run_agent_structured("Что такое Python?", provider=provider)
            assert isinstance(response, AgentResponse)
            assert response.answer
            print(f"✅ {provider}: OK")
        except ValueError as e:
            if "не найден" in str(e) or "OPENROUTER" in str(e):
                pytest.skip(f"Нет ключа для {provider}")
            raise
