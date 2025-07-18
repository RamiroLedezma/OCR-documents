import base64
import io
import json
import os
import re
from PIL import Image
from pdf2image import convert_from_bytes
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener API Key desde el entorno
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la variable OPENAI_API_KEY en el entorno")

# Cliente de OpenAI con clave explícita
client = OpenAI(api_key=api_key)

def extract_info_from_base64(base64_str):
    # Decodificar base64
    file_bytes = base64.b64decode(base64_str)
    images = []

    # Intentar abrir como imagen
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        images.append(img)
    except Exception:
        # Si no es imagen, intentar como PDF
        try:
            images = convert_from_bytes(file_bytes, dpi=200)
        except Exception as e:
            raise ValueError("No se pudo procesar el archivo como imagen ni como PDF.") from e

    if not images:
        raise ValueError("No se extrajeron imágenes del archivo.")

    # Convertir cada imagen a base64
    image_payloads = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        image_payloads.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })

    # Instrucciones para GPT
    prompt = """
Eres un sistema de lectura de documentos de identidad (cédula o pasaporte).
Extrae los siguientes campos y devuélvelos en un JSON como este:

{
  "tipo": "cedula" o "pasaporte",
  "campos": {
    "nombres": "...",
    "apellidos": "...",
    "numero_documento": "...",
    "fecha_nacimiento": "...",
    "fecha_expedicion": "...",
    "sexo": "...",
    "grupo_sanguineo": "...",
    "lugar_nacimiento": "...",
    "estatura": "..."
  }
}

Si no se puede determinar algún campo, déjalo vacío.
    """

    # Enviar múltiples imágenes al modelo
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": image_payloads}
        ],
        max_tokens=800
    )

    content = response.choices[0].message.content.strip()

    # Sanitización del resultado
    cleaned = clean_code_block(content)
    formatted = format_dict_keys_and_values(cleaned)
    try:
        result = json.loads(formatted)
        return result
    except Exception:
        raise ValueError("La respuesta de OpenAI no fue un JSON válido:\n" + content)

# Helpers
def clean_code_block(text):
    return re.sub(r'```[a-zA-Z]*', '', text).replace('```', '').strip()

def format_dict_keys_and_values(text):
    text = text.replace("dict(", "{").replace(")", "}")
    text = re.sub(r'(\w+)=', r'"\1":', text)
    return text
