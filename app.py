from fastapi import FastAPI
from pydantic import BaseModel
import base64
import uuid
import os
from src.utils.ocr_openai import extract_text_and_fields_with_openai
from src.utils.parser import extract_entities
from src.extractor.model import save_to_database
from typing import List, Optional
from pdf2image import convert_from_bytes
from PIL import Image
import io

app = FastAPI()

class DocumentRequest(BaseModel):
    filename: str
    file_base64: Optional[str] = None  # Para compatibilidad con requests antiguos
    files_base64: Optional[List[str]] = None  # Para múltiples imágenes (frente y respaldo)

# Utilidad para PDF
def get_images_base64_from_pdf(pdf_bytes: bytes) -> List[str]:
    images = convert_from_bytes(pdf_bytes)
    if len(images) > 2:
        raise ValueError("El PDF debe tener máximo 2 páginas: frente y respaldo.")
    base64_list = []
    for img in images:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        base64_list.append(base64.b64encode(img_byte_arr.getvalue()).decode())
    return base64_list

def get_image_base64_from_image(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    img_byte_arr = io.BytesIO()
    img = img.convert('RGB')
    img.save(img_byte_arr, format='JPEG')
    return base64.b64encode(img_byte_arr.getvalue()).decode()

@app.post("/extract")
async def extract_info(doc: DocumentRequest):
    # Detecta extensión
    ext = os.path.splitext(doc.filename)[1].lower()
    all_images_base64 = []

    if ext == '.pdf':
        if not doc.file_base64:
            return {"error": "El campo file_base64 es obligatorio para archivos PDF."}
        file_bytes = base64.b64decode(doc.file_base64)
        try:
            all_images_base64 = get_images_base64_from_pdf(file_bytes)
        except ValueError as e:
            return {"error": str(e)}
    elif ext in ['.png', '.jpg', '.jpeg']:
        # Soporta lista de imágenes o una sola
        if doc.files_base64:
            for img_b64 in doc.files_base64:
                img_bytes = base64.b64decode(img_b64)
                all_images_base64.append(get_image_base64_from_image(img_bytes))
        elif doc.file_base64:
            img_bytes = base64.b64decode(doc.file_base64)
            all_images_base64.append(get_image_base64_from_image(img_bytes))
        else:
            return {"error": "Debes enviar al menos una imagen en base64."}
    else:
        return {"error": "Formato de archivo no soportado. Usa PDF, PNG o JPG."}

    # Guarda los archivos originales (opcional)
    os.makedirs("uploads", exist_ok=True)
    if ext == '.pdf':
        if not doc.file_base64:
            return {"error": "El campo file_base64 es obligatorio para archivos PDF."}
        filepath = f"uploads/{uuid.uuid4()}_{doc.filename}"
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(doc.file_base64))
    else:
        for idx, img_b64 in enumerate(all_images_base64):
            filepath = f"uploads/{uuid.uuid4()}_{idx}_{doc.filename}"
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(img_b64))

    # OCR + Extraction para todas las caras
    full_text = ""
    ocr_results = []
    for img_b64 in all_images_base64:
        result = extract_text_and_fields_with_openai(img_b64)
        ocr_results.append(result)
        full_text += (result.get("texto_legible") or "") + "\n"
    # Combina todos los resultados para la extracción de entidades
    entities = extract_entities(full_text, raw_data=ocr_results[0] if ocr_results else {})

    # Validación de legibilidad
    advertencias = []
    if not full_text or len(full_text.strip()) < 10:
        advertencias.append("Advertencia: El texto extraído es muy corto o ilegible. Verifique la calidad de la imagen.")
    if "advertencia_tipo_documento" in entities:
        advertencias.append(entities["advertencia_tipo_documento"])

    # Save to DB
    save_to_database(entities, full_text)

    return {
        "tipo_documento": entities.get("tipo_documento", "Desconocido"),
        "texto_legible": full_text,
        "datos": entities,
        "advertencias": advertencias if advertencias else None
    }
