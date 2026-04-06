from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text, func
from sqlalchemy.orm import relationship
from backend.database import Base

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    hash_pdf = Column(Text, nullable=False)
    imagen_asociada = Column(String(255), nullable=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())

    verificaciones = relationship("Verificacion", back_populates="documento")

class Verificacion(Base):
    __tablename__ = "verificaciones"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    resultado = Column(Boolean, nullable=False)
    fecha_verificacion = Column(TIMESTAMP, server_default=func.now())

    documento = relationship("Documento", back_populates="verificaciones")


class Imagen(Base):
    __tablename__ = "imagenes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)  # Aquí se guarda la URL de la imagen
    salt = Column(String, nullable=True)        # Para guardar el salt asociado
