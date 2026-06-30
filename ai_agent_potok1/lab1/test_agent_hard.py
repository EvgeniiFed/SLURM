"""Тесты Hard: Fallback + Cost Tracking."""

import pytest
import socket

from agent import (
    run_agent, run_agent_structured, create_agent,
    check_litellm_proxy
)
from config import get_cost_report, get_litellm_spend_logs
from tools import DeleteBlocker
from models import AgentResponse


# ========== Fallback Chain ==========

def test_litellm_proxy_available():
    """LiteLLM proxy запущен."""
    assert check_litellm_proxy(), "LiteLLM proxy не запущен на localhost:4000"


def test_agent_works_through_litellm():
    """Агент работает через LiteLLM (primary)."""
    result = run_agent("Что такое Python?", provider="litellm")
    assert "structured" in result
    assert isinstance(result["structured"], AgentResponse)


def test_fallback_models_configured():
    """Fallback модели настроены в LiteLLM."""
    import requests
    response = requests.get(
        "http://localhost:4000/v1/models",
        headers={"Authorization": "Bearer sk-litellm-master-key-123"},
        timeout=5,
    )
    assert response.status_code == 200
    data = response.json()
    model_ids = [m["id"] for m in data.get("data", [])]
    assert "agent-llm" in model_ids
    assert "agent-llm-fallback" in model_ids


# ========== Cost Tracking ==========

def test_cost_report_available():
    """Cost tracking через OpenRouter работает."""
    report = get_cost_report()
    assert isinstance(report, dict)
    assert "openrouter" in report


def test_litellm_logs_endpoint_exists():
    """Эндпоинт /spend/logs доступен (может быть пустым)."""
    logs = get_litellm_spend_logs()
    assert isinstance(logs, dict)


def test_cost_tracking_after_request():
    """После запроса cost tracking работает."""
    # Безопасный запрос, который точно не триггерит delete
    run_agent("Расскажи про язык программирования Python", provider="litellm")
    report = get_cost_report()
    assert isinstance(report, dict)

# ========== Совместимость с Min/Medium ==========

def test_structured_output_hard():
    """Structured output работает в Hard."""
    response = run_agent_structured("Python", provider="litellm")
    assert isinstance(response, AgentResponse)
    assert response.answer


def test_delete_blocked_hard():
    """Блокировка delete работает в Hard."""
    with pytest.raises(PermissionError):
        run_agent("Удали всё", provider="litellm")
