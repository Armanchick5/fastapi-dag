from pydantic import BaseModel, Field, validator
from typing import List, Dict


class NodeBase(BaseModel):
    name: str = Field(..., max_length=255)

    @validator('name')
    def must_be_latin(cls, v):
        if not v.isascii() or not v.isalnum():
            raise ValueError('Имя узла должно быть латиницей и цифрами')
        return v


class EdgeBase(BaseModel):
    source: str
    target: str


class GraphCreate(BaseModel):
    nodes: List[NodeBase]
    edges: List[EdgeBase]


class GraphCreateResponse(BaseModel):
    id: int


class GraphRead(BaseModel):
    id: int
    nodes: List[NodeBase]
    edges: List[EdgeBase]


class AdjacencyListResponse(BaseModel):
    adjacency_list: Dict[str, List[str]]


class ErrorResponse(BaseModel):
    message: str
