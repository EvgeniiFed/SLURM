# 🤖 AI Agent — Домашнее задание (Min / Medium / Hard)

Read-only агент с кастомным инструментом, блокировкой delete-операций, LiteLLM proxy, fallback chain и cost tracking.

---

## 📋 Содержание

- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Уровни реализации](#уровни-реализации)
  - [Min](#min-read-only--custom-tool--delete-hook)
  - [Medium](#medium-litellm-proxy--structured-output)
  - [Hard](#hard-fallback-chain--cost-tracking)
- [Провайдеры LLM](#провайдеры-llm)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)
- [API и эндпоинты](#api-и-эндпоинты)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        Пользователь                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    LiteLLM Proxy :4000                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐ │
│  │ DeepSeek v4 │───►│ DeepSeek    │───►│ GPT-4o mini     │ │
│  │ (AI Router) │fail│ (AI Router) │fail│ (OpenRouter)    │ │
│  └─────────────┘    └─────────────┘    └─────────────────┘ │
│                                                │            │
│                                                ▼            │
│                                       ┌─────────────────┐   │
│                                       │ DeepSeek free   │   │
│                                       │ (OpenRouter)    │   │
│                                       └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Read-only Агент                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │ my_search   │    │ DeleteBlocker│    │ AgentResponse   │  │
│  │ (custom     │    │ (hook)       │    │ (Pydantic JSON) │  │
│  │  tool)      │    │              │    │                 │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### 1. Клонирование и настройка окружения

```bash
git clone <repo-url>
cd ai_agent_potok1/lab1

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Настройка API-ключей

```bash
cp .env.example .env
# Редактируем .env
nano .env
```

```env
# Обязательно: хотя бы один ключ
AIROUTER_API_KEY=sk-ваш-ключ-ai-router
OPENROUTER_API_KEY=sk-or-v1-ваш-ключ-openrouter

# Опционально: нативные провайдеры
# DASHSCOPE_API_KEY=sk-ваш-ключ-qwen
# MOONSHOT_API_KEY=sk-ваш-ключ-kimi
# DEEPSEEK_API_KEY=sk-ваш-ключ-deepseek
```

### 3. Запуск LiteLLM proxy (для Medium/Hard)

```bash
litellm --config litellm_config.yaml --port 4000
```

### 4. Запуск тестов

```bash
# Все уровни
pytest -v

# Только Min
pytest test_agent.py -v

# Только Medium
pytest test_agent_medium.py -v

# Только Hard
pytest test_agent_hard.py -v

# Без warnings
pytest -v --disable-warnings
```

---

## 📊 Уровни реализации

### Min: Read-only + Custom Tool + Delete Hook

**Что реализовано:**
- ✅ Read-only агент (не может модифицировать данные)
- ✅ Кастомный инструмент `my_search` (поиск по базе знаний)
- ✅ Блокировка delete-операций через `DeleteBlocker`
- ✅ Подключение к LLM через AI Router (DeepSeek)

**Ключевые файлы:** `tools.py`, `agent.py`, `test_agent.py`

**Запуск:**
```bash
python agent.py  # provider = "airouter" по умолчанию
```

---

### Medium: LiteLLM Proxy + Structured Output

**Что добавлено:**
- ✅ LiteLLM proxy на `localhost:4000`
- ✅ Единый endpoint для всех моделей
- ✅ Pydantic structured output (`AgentResponse`)
- ✅ Предсказуемый JSON: `answer`, `confidence`, `is_safe`, `tools_called`

**Ключевые файлы:** `litellm_config.yaml`, `models.py`, `test_agent_medium.py`

**Запуск:**
```bash
# Терминал 1
litellm --config litellm_config.yaml --port 4000

# Терминал 2
python agent.py  # provider = "litellm" (автоопределение)
```

**Формат ответа:**
```json
{
  "answer": "Python — язык программирования...",
  "sources_used": ["my_search"],
  "confidence": 0.95,
  "is_safe": true,
  "tools_called": ["my_search"]
}
```

---

### Hard: Fallback Chain + Cost Tracking

**Что добавлено:**
- ✅ Fallback chain: 4 модели с автопереключением при сбое
- ✅ Cost tracking через OpenRouter API
- ✅ Отчёт по расходам: баланс, использовано, статистика

**Fallback chain:**
| Приоритет | Модель | Провайдер | Роль |
|-----------|--------|-----------|------|
| 1 | DeepSeek v4 Flash | AI Router | Primary |
| 2 | DeepSeek Chat | AI Router | Fallback 1 |
| 3 | GPT-4o mini | OpenRouter | Fallback 2 |
| 4 | DeepSeek Chat | OpenRouter | Emergency |

**Ключевые файлы:** `config.py` (cost tracking), `test_agent_hard.py`

**Cost tracking:**
```python
from config import print_cost_report
print_cost_report()
```

**Пример вывода:**
```
============================================================
=== 💰 COST REPORT ===
============================================================

--- OpenRouter ---
Баланс: $375.00
Использовано: $0.54
Запросов: 12

--- LiteLLM ---
Статус: Без БД логи не хранятся
```

---

## 🔌 Провайдеры LLM

| Провайдер | Модели | Способ подключения | Ключ |
|-----------|--------|-------------------|------|
| **AI Router** | DeepSeek v4, DeepSeek Chat | Прямое / LiteLLM | `AIROUTER_API_KEY` |
| **OpenRouter** | GPT-4o, Claude, Llama, Mistral | Прямое / LiteLLM | `OPENROUTER_API_KEY` |
| **Qwen** | qwen-max, qwen-plus | Нативное | `DASHSCOPE_API_KEY` |
| **Kimi** | kimi-latest, kimi-k2 | Нативное | `MOONSHOT_API_KEY` |
| **DeepSeek** | deepseek-chat | Нативное | `DEEPSEEK_API_KEY` |

**Переключение провайдера:**
```python
# Через LiteLLM proxy (рекомендуется)
run_agent("Вопрос", provider="litellm")

# Напрямую через AI Router
run_agent("Вопрос", provider="airouter")

# Напрямую через OpenRouter
run_agent("Вопрос", provider="openrouter")
run_agent("Вопрос", provider="openrouter:anthropic/claude-3.5-sonnet")

# Нативные (если ключи есть)
run_agent("Вопрос", provider="deepseek")
run_agent("Вопрос", provider="qwen")
run_agent("Вопрос", provider="kimi")
```

---

## 🧪 Тестирование

### Запуск всех тестов

```bash
pytest test_agent.py test_agent_medium.py test_agent_hard.py test_agent_openrouter.py -v
```

### Результаты

```
test_agent.py::test_search_tool_works PASSED
test_agent.py::test_delete_blocked_english PASSED
test_agent.py::test_delete_blocked_russian PASSED
test_agent.py::test_safe_query_passes PASSED
test_agent.py::test_agent_can_answer PASSED
test_agent.py::test_agent_blocks_delete PASSED
test_agent.py::test_agent_blocks_delete_russian PASSED
test_agent.py::test_create_agent_airouter PASSED
test_agent.py::test_agent_can_answer_native[deepseek] SKIPPED  # нет ключа
test_agent.py::test_agent_can_answer_native[qwen] SKIPPED      # нет ключа
test_agent.py::test_agent_can_answer_native[kimi] SKIPPED      # нет ключа
...

=================== 28 passed, 6 skipped in ~160s ===================
```

### Покрытие по уровням

| Уровень | Тесты | Покрытие |
|---------|-------|----------|
| Min | 8 + 6 параметризованных | Инструменты, блокировка, агент |
| Medium | 8 | Structured output, LiteLLM proxy |
| Hard | 8 | Fallback, cost tracking |
| OpenRouter | 4 | Прямое подключение, все модели |

---

## 📁 Структура проекта

```
ai-agent-hw/
├── .env                          # API-ключи (не коммитить!)
├── .env.example                  # Шаблон ключей
├── requirements.txt              # Python-зависимости
├── README.md                     # Этот файл
│
├── litellm_config.yaml           # Конфиг LiteLLM proxy
│
├── models.py                     # Pydantic-схемы (AgentResponse)
├── config.py                     # Фабрика LLM + cost tracking
├── tools.py                      # Custom tool + DeleteBlocker
├── agent.py                      # Основной агент + демо
│
├── test_agent.py                 # Тесты Min (8 тестов)
├── test_agent_medium.py          # Тесты Medium (8 тестов)
├── test_agent_hard.py            # Тесты Hard (8 тестов)
└── test_agent_openrouter.py      # Тесты OpenRouter (4 теста)
```

---

## 🔌 API и эндпоинты

### LiteLLM Proxy (localhost:4000)

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/v1/models` | GET | Список доступных моделей |
| `/v1/chat/completions` | POST | Chat completions (OpenAI-совместимый) |
| `/spend/logs` | GET | Логи расходов (требует БД) |
| `/spend/keys` | GET | Расходы по API-ключам |

**Пример запроса:**
```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-litellm-master-key-123" \
  -d '{
    "model": "agent-llm",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### OpenRouter API

| Эндпоинт | Описание |
|----------|----------|
| `https://openrouter.ai/api/v1/credits` | Баланс и кредиты |
| `https://openrouter.ai/api/v1/usage` | История использования |
| `https://openrouter.ai/api/v1/generation` | Статистика генераций |

---

## ⚠️ Известные ограничения

1. **LiteLLM БД**: Для полного cost tracking в LiteLLM требуется PostgreSQL + Prisma. В текущей реализации используется OpenRouter API для отслеживания расходов.
2. **Warnings**: `langchain-core` 0.2.x выдаёт deprecation warnings от Pydantic v2. Это внутреннее, не влияет на работу.
3. **Rate limits**: Зависят от провайдера (AI Router, OpenRouter).

---

## 🔧 Требования

- Python 3.12+
- Ubuntu 24.04 (тестировалось)
- 2 vCPU, 4 GB RAM (для LiteLLM proxy)
- API-ключи: AI Router и/или OpenRouter

---

## 📚 Использованные технологии

- **LangChain** — фреймворк для агентов
- **Pydantic v2** — валидация и structured output
- **LiteLLM** — универсальный proxy для LLM
- **pytest** — тестирование
- **OpenRouter / AI Router** — доступ к моделям
