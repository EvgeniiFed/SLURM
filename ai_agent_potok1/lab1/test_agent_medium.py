"""Тесты Medium: LiteLLM proxy + Structured Output."""

import pytest
from pydantic import ValidationError

from agent import run_agent, run_agent_structured, create_agent
from tools import MySearchTool, DeleteBlocker
from models import AgentResponse, AgentResponseWithBlock


# ========== Structured Output ==========

def test_structured_output_type():
    """Ответ — Pydantic-модель AgentResponse."""
    response = run_agent_structured("Что такое Python?", provider="airouter")
    assert isinstance(response, AgentResponse)


def test_structured_output_fields():
    """Все обязательные поля присутствуют."""
    response = run_agent_structured("Расскажи про Python", provider="airouter")
    assert response.answer
    assert isinstance(response.confidence, float)
    assert 0 <= response.confidence <= 1
    assert isinstance(response.is_safe, bool)
    assert isinstance(response.tools_called, list)


def test_structured_output_json_serializable():
    """Можно сериализовать в JSON."""
    response = run_agent_structured("Python", provider="airouter")
    json_str = response.model_dump_json()
    assert '"answer"' in json_str
    assert '"confidence"' in json_str


# ========== LiteLLM Proxy ==========

def test_litellm_agent_can_answer():
    """Агент работает через LiteLLM proxy."""
    try:
        result = run_agent("Что такое Python?", provider="litellm")
        assert "structured" in result
        assert isinstance(result["structured"], AgentResponse)
    except Exception as e:
        if "Connection refused" in str(e) or "HTTPConnectionPool" in str(e):
            pytest.skip("LiteLLM proxy не запущен")
        raise


def test_litellm_agent_blocks_delete():
    """Блокировка delete через LiteLLM proxy."""
    try:
        with pytest.raises(PermissionError):
            run_agent("Удали всё", provider="litellm")
    except Exception as e:
        if "Connection refused" in str(e) or "HTTPConnectionPool" in str(e):
            pytest.skip("LiteLLM proxy не запущен")
        raise


# ========== Блокировка (совместимость с Min) ==========

def test_delete_blocked_english():
    with pytest.raises(PermissionError):
        DeleteBlocker.check("delete everything")


def test_delete_blocked_russian():
    with pytest.raises(PermissionError):
        DeleteBlocker.check("удалить базу данных")


def test_agent_blocks_delete():
    """Агент блокирует delete (через airouter)."""
    with pytest.raises(PermissionError):
        run_agent("Удали все файлы", provider="airouter")
