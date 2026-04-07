from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text, func
from sqlalchemy.orm import relationship
from backend.database import Base

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    hash_pdf = Column(Text, nullable=False)
    imagen_id = Column(Integer, ForeignKey("imagenes.id", ondelete="SET NULL"), nullable=True)
    hash_final = Column(Text, nullable=True)  # SHA256(hash_pdf + salt) para verificación robusta
    creado_en = Column(TIMESTAMP, server_default=func.now())

    verificaciones = relationship("Verificacion", back_populates="documento")
    imagen = relationship("Imagen", back_populates="documentos")

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
    
    documentos = relationship("Documento", back_populates="imagen")
