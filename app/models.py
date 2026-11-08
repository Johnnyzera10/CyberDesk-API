from typing import Literal

from pydantic import BaseModel, Field

class IncidenteBase(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    descricao: str = Field(min_length=5)
    categoria: str = Field(min_length=3, max_length=50)
    severidade: Literal["Baixa", "Media", "Alta", "Critica"]

class IncidenteCreate(IncidenteBase):
    pass

class IncidenteUpdate(IncidenteBase):
    status: Literal["Aberto", "Em analise", "Resolvido"]

