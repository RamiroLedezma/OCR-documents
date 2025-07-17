from typing import Optional, Dict, Any, Tuple, Union
from src.utils.validators import DocumentValidator
from src.utils.logger import logger

TIPOS_VALIDOS = [
    "cedula amarilla",
    "cedula digital",
    "cedula de extranjeria",
    "pasaporte"
]

# Patrones para identificar tipos de documento
TIPO_PATRONES = {
    "cedula amarilla": ["cédula de ciudadanía", "cedula de ciudadania", "cedula amarilla", "cédula amarilla"],
    "cedula digital": ["cédula digital", "cedula digital"],
    "cedula de extranjeria": ["cédula de extranjería", "cedula de extranjeria", "cédula de extranjeria"],
    "pasaporte": ["pasaporte"]
}

# Lista de todos los campos requeridos
CAMPOS_REQUERIDOS = [
    "numero_documento",
    "apellidos",
    "nombres",
    "fecha_nacimiento",
    "lugar_nacimiento",
    "estatura",
    "grupo_sanguineo",
    "sexo",
    "fecha_expedicion",
    "lugar_expedicion"
]

def detectar_tipo_documento(text: str) -> Tuple[str, Optional[str]]:
    text_lower = text.lower()
    for tipo, patrones in TIPO_PATRONES.items():
        for patron in patrones:
            if patron in text_lower:
                return tipo, None
    return "desconocido", "Tipo de documento no reconocido o no soportado."

def extract_entities(text: str, raw_data: Optional[Dict[str, Any]] = None) -> Dict[str, Union[str, None]]:
    """
    Extrae todos los campos requeridos y los deja en None si no se encuentran.
    """
    advertencia = None
    entities: Dict[str, Union[str, None]] = {campo: None for campo in CAMPOS_REQUERIDOS}
    if raw_data is not None:
        logger.debug("Validando datos extraídos de OpenAI", raw_data=raw_data)
        validated = DocumentValidator.validate_extracted_data(raw_data)
        for campo in CAMPOS_REQUERIDOS:
            if campo in validated:
                entities[campo] = validated[campo]
        tipo_detectado, advertencia = detectar_tipo_documento(text)
        entities["tipo_documento"] = tipo_detectado
    else:
        import re
        # Patrones flexibles para cada campo
        entities["numero_documento"] = extract_field(text, r"(n[úu]mero\s*[:\-]?|documento\s*[:\-]?|no\.?\s*[:\-]?|num\.?\s*[:\-]?|identidad\s*[:\-]?|doc\.?\s*[:\-]?)[\s\n]*([A-Z0-9\-]+)", group=2)
        entities["apellidos"] = extract_field(text, r"apellidos?\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+)", flags=re.IGNORECASE)
        entities["nombres"] = extract_field(text, r"nombres?\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+)", flags=re.IGNORECASE)
        entities["fecha_nacimiento"] = extract_field(text, r"(fecha\s*(de)?\s*nacimiento|f\.?\s*nac\.?|nacido el)\s*[:\-]?\s*([0-9]{2,4}[\/\-][0-9]{2}[\/\-][0-9]{2,4})", group=3)
        entities["lugar_nacimiento"] = extract_field(text, r"(lugar\s*(de)?\s*nacimiento|nacido en)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+)", group=3, flags=re.IGNORECASE)
        entities["estatura"] = extract_field(text, r"estatura\s*[:\-]?\s*([\d\.]+\s*(cm|m)?)", flags=re.IGNORECASE)
        entities["grupo_sanguineo"] = extract_field(text, r"grupo sangu[íi]neo\s*[:\-]?\s*([A|B|AB|O][+-])", flags=re.IGNORECASE)
        entities["sexo"] = extract_field(text, r"(sexo|género|genero)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+)", group=2, flags=re.IGNORECASE)
        entities["fecha_expedicion"] = extract_field(text, r"(fecha\s*(de)?\s*expedici[óo]n|f\.?\s*exp\.?|expedido el)\s*[:\-]?\s*([0-9]{2,4}[\/\-][0-9]{2}[\/\-][0-9]{2,4})", group=3)
        entities["lugar_expedicion"] = extract_field(text, r"(lugar\s*(de)?\s*expedici[óo]n|expedido en)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s]+)", group=3, flags=re.IGNORECASE)
        tipo_detectado, advertencia = detectar_tipo_documento(text)
        entities["tipo_documento"] = tipo_detectado
    if advertencia:
        entities["advertencia_tipo_documento"] = advertencia
    return entities

def extract_field(text, pattern, group=1, flags=0):
    import re
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else None
