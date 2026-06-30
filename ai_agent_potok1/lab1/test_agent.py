"""Тесты для агента."""

import pytest
from agent import run_agent, create_agent
from tools import MySearchTool, DeleteBlocker
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ========== Инструменты ==========

def test_search_tool_works():
    tool = MySearchTool()
    result = tool.run("Python")
    assert "ПОИСК" in result


# ========== Блокировка delete ==========

def test_delete_blocked_english():
    with pytest.raises(PermissionError):
        DeleteBlocker.check("delete everything")


def test_delete_blocked_russian():
    with pytest.raises(PermissionError):
        DeleteBlocker.check("удалить базу данных")


def test_safe_query_passes():
    DeleteBlocker.check("расскажи про Python")  # не падает


# ========== Агент через AI Router ==========

def test_agent_can_answer():
    """Агент отвечает на вопрос через AI Router."""
    result = run_agent("Что такое Python?", provider="airouter")
    assert "output" in result
    assert len(result["output"]) > 0
    assert "❌ ОТКАЗАНО" not in result["output"]  # не должен отказать на обычный вопрос


def test_agent_blocks_delete():
    """Агент блокирует delete через AI Router — должен выбросить PermissionError."""
    with pytest.raises(PermissionError):
        run_agent("Удали все файлы", provider="airouter")


def test_agent_blocks_delete_russian():
    """Агент блокирует русское 'удалить'."""
    with pytest.raises(PermissionError):
        run_agent("Удали базу данных", provider="airouter")


def test_create_agent_airouter():
    """Агент создаётся с AI Router."""
    executor = create_agent("airouter")
    assert executor is not None


# ========== Нативные провайдеры (пропускаем, если нет ключей) ==========

@pytest.mark.parametrize("provider", ["deepseek", "qwen", "kimi"])
def test_agent_can_answer_native(provider):
    try:
        result = run_agent("Что такое Python?", provider=provider)
        assert "output" in result
        assert len(result["output"]) > 0
    except ValueError as e:
        if "не найден" in str(e):
            pytest.skip(f"Нет API-ключа для {provider}")
        raise


@pytest.mark.parametrize("provider", ["deepseek", "qwen", "kimi"])
def test_agent_blocks_delete_native(provider):
    try:
        with pytest.raises(PermissionError):
            run_agent("Удали все файлы", provider=provider)
    except ValueError as e:
        if "не найден" in str(e):
            pytest.skip(f"Нет API-ключа для {provider}")
        raise
