from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import Optional
import pytz

def _to_bogota_time(dt):
    """Convierte datetime UTC a zona horaria de Bogotá"""
    if dt is None:
        return None
    bogota_tz = pytz.timezone("America/Bogota")
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(bogota_tz)

# ------------------------------
# Schemas para Documentos
# ------------------------------
class DocumentoBase(BaseModel):
    nombre: str
    hash_pdf: str
    imagen_id: int
    hash_final: Optional[str] = None

class DocumentoCreate(DocumentoBase):
    pass

class Documento(DocumentoBase):
    id: int
    creado_en: datetime

    @field_serializer('creado_en')
    def serialize_creado_en(self, value: datetime) -> str:
        """Serializa creado_en a zona horaria de Bogotá"""
        return str(_to_bogota_time(value))

    class Config:
        from_attributes = True


# ------------------------------
# Schemas para Verificaciones
# ------------------------------
class VerificacionBase(BaseModel):
    documento_id: int
    resultado: bool

class VerificacionCreate(VerificacionBase):
    pass

class Verificacion(VerificacionBase):
    id: int
    fecha_verificacion: datetime

    @field_serializer('fecha_verificacion')
    def serialize_fecha_verificacion(self, value: datetime) -> str:
        """Serializa fecha_verificacion a zona horaria de Bogotá"""
        return str(_to_bogota_time(value))

    class Config:
        from_attributes = True


# ------------------------------
# Schemas para Imagenes
# ------------------------------

class ImagenBase(BaseModel):
    nombre: str
    url: str

class ImagenCreate(ImagenBase):
    pass

class Imagen(ImagenBase):
    id: int

    class Config:
        from_attributes = True
