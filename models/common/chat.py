from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "model", "system", "assistant", "function"]
    content: str
