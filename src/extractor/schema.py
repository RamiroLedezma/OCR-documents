from pydantic import BaseModel
from typing import Optional, Dict


# Esquema para la solicitud POST /extract
class DocumentRequest(BaseModel):
    filename: str
    file_base64: str


# Esquema para los datos extraídos
class ExtractedData(BaseModel):
    tipo_documento: Optional[str]
    numero_documento: Optional[str]
    nombres: Optional[str]
    apellidos: Optional[str]
    fecha_nacimiento: Optional[str]
    lugar_nacimiento: Optional[str]
    estatura: Optional[str]
    grupo_sanguineo: Optional[str]
    sexo: Optional[str]
    fecha_expedicion: Optional[str]
    lugar_expedicion: Optional[str]


# Esquema para la respuesta del API
class DocumentResponse(BaseModel):
    tipo_documento: str
    texto_legible: str
    datos: Dict[str, Optional[str]]
