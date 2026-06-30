"""Свои инструменты для агента."""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    """Входные данные для поиска."""
    query: str = Field(description="Что искать")


class MySearchTool(BaseTool):
    """Простой поисковый инструмент."""
    
    name: str = "my_search"
    description: str = "Ищет информацию по запросу."
    args_schema: type[BaseModel] = SearchInput
    
    def _run(self, query: str) -> str:
        return f"[ПОИСК] Результаты по '{query}': Python — язык программирования."
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class DeleteBlocker:
    """Блокирует опасные операции."""
    
    FORBIDDEN = ["delete", "удалить", "drop", "очистить", "стереть", "remove all"]
    
    @classmethod
    def check(cls, text: str) -> None:
        text_lower = text.lower()
        for word in cls.FORBIDDEN:
            if word in text_lower:
                raise PermissionError(f"🚫 Заблокировано: '{word}'")
