import openai
from dotenv import load_dotenv
import os
from src.config import settings
from src.utils.logger import ocr_logger

load_dotenv()
openai.api_key = settings.OPENAI_API_KEY

def extract_text_and_fields_with_openai(base64_image: str) -> dict:
    messages = [
        {"role": "system", "content": (
            "Eres un extractor de datos de documentos de identidad colombianos. "
            "Recibes una imagen de un documento (cédula de ciudadanía, cédula digital, cédula de extranjería o pasaporte). "
            "Devuelve un JSON con los siguientes campos SIEMPRE presentes (aunque sean null): "
            "tipo_documento, numero_documento, nombres, apellidos, fecha_nacimiento, lugar_nacimiento, estatura, grupo_sanguineo, sexo, fecha_expedicion, lugar_expedicion, texto_legible. "
            "Busca variantes de etiquetas y formatos, y si un campo no está explícito, intenta inferirlo del contexto. "
            "Si no puedes inferir un campo, pon null. "
            "Ignora errores menores de OCR y responde SOLO con un JSON válido."
        )},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Extrae todos los campos del documento y responde SOLO con un JSON válido. "
                    "Incluye los campos aunque no estén presentes en el documento. "
                    "Ejemplo de respuesta: {\"tipo_documento\":..., \"numero_documento\":..., ...}"
                )},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )
        content = response.choices[0].message.content
        usage = getattr(response, "usage", None)
        tokens_used = usage.total_tokens if usage and getattr(usage, "total_tokens", None) else None
        ocr_logger.ocr_request(
            image_size=len(base64_image),
            model=settings.OPENAI_MODEL,
            tokens_used=tokens_used
        )
        # Intentar extraer JSON del contenido
        import json
        try:
            if content and content.strip().startswith('{'):
                return json.loads(content)
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL) if content else None
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError('No se encontró JSON en la respuesta de OpenAI')
        except Exception as e:
            ocr_logger.error("Error parsing OpenAI JSON response", error=e, raw_content=content)
            raise
    except Exception as e:
        ocr_logger.error("Error in OpenAI OCR extraction", error=e)
        raise
