import asyncio

from typing import Optional, List

from pydantic import BaseModel, UUID4, Field, Base64Str

from .property import Property


class Player(BaseModel):
    id: Optional[UUID4] = None
    name: str = Field(..., min_length=2, max_length=16)
    properties: List[Property] = []
    profileActions: List[str] = []
    protocolVersion: int
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    class Config:
        arbitrary_types_allowed = True
