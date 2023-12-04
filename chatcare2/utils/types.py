# coding=utf-8
import time
from typing import Any, Dict, List, Literal, Optional, Union, Tuple
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = "腰椎间盘突出没做手术如何护理?"


class ChatKnowledgeBaseRequest(BaseModel):
    messages: List[ChatMessage]

class ChatKnowledgeBaseResponse(BaseModel):
    error: int = 0
    summary: str = ''
    intent_id: int = 0
    hints: List[str] = []
    details: List[Tuple[str,List[Dict]]] = []
