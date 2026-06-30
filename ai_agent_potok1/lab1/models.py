"""Pydantic-модели для structured output."""

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """
    Строгий формат ответа агента.
    Агент ВСЕГДА должен возвращать JSON, соответствующий этой схеме.
    """
    
    answer: str = Field(
        description="Ответ пользователю на его вопрос",
        min_length=1,
    )
    
    sources_used: list[str] = Field(
        description="Список использованных источников (если искали)",
        default_factory=list,
    )
    
    confidence: float = Field(
        description="Уверенность в ответе от 0.0 до 1.0",
        ge=0.0,
        le=1.0,
        default=0.8,
    )
    
    is_safe: bool = Field(
        description="Прошла ли проверка безопасности (read-only)",
        default=True,
    )
    
    tools_called: list[str] = Field(
        description="Список вызванных инструментов",
        default_factory=list,
    )


class AgentResponseWithBlock(BaseModel):
    """
    Ответ при блокировке (delete-запрос).
    """
    
    answer: str = Field(
        description="Сообщение об отказе",
        default="❌ ОТКАЗАНО: read-only агент не может выполнять delete-операции.",
    )
    
    is_safe: bool = Field(default=False)
    blocked_reason: str = Field(default="delete_operation_detected")
