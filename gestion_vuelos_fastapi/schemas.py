from pydantic import BaseModel
from datetime import datetime
from models import EstadoVuelo

class VueloBase(BaseModel):
    codigo: str
    estado: EstadoVuelo
    hora: datetime
    origen: str
    destino: str

class VueloCreate(VueloBase):
    pass

class VueloOut(VueloBase):
    class Config:
        orm_mode = True