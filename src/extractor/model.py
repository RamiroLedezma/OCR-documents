from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from src.extractor.database import SessionLocal
from src.utils.logger import db_logger

Base = declarative_base()   

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String(50))
    numero_documento = Column(String(30))
    nombres = Column(String(100))
    apellidos = Column(String(100))
    texto_legible = Column(Text)

def save_to_database(entities, full_text):
    db = SessionLocal()
    try:
        doc = Documento(
            tipo_documento=entities.get("tipo_documento"),
            numero_documento=entities.get("numero_documento"),
            nombres=entities.get("nombres"),
            apellidos=entities.get("apellidos"),
            texto_legible=full_text
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db_logger.database_operation(
            operation="insert",
            table="documentos",
            success=True,
            duration=0  # Puedes medir el tiempo si lo deseas
        )
        return doc
    except SQLAlchemyError as e:
        db.rollback()
        db_logger.database_operation(
            operation="insert",
            table="documentos",
            success=False,
            duration=0,
            error=str(e)
        )
        raise
    finally:
        db.close()
