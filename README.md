# Extracción de Datos de Documentos de Identidad

Este proyecto implementa un servicio web HTTP REST (API) para la extracción de entidades de documentos de identificación colombianos (Cédula de Ciudadanía, Cédula Digital, Cédula de Extranjería, Pasaporte) y almacenamiento en una base de datos MySQL.

## Características
- Recibe archivos en formato PDF (máx. 2 páginas), JPG o PNG (frente y respaldo).
- Los archivos se envían codificados en base64.
- Extrae y valida los siguientes campos:
  - Número de documento
  - Apellidos
  - Nombres
  - Fecha de nacimiento
  - Lugar de nacimiento
  - Estatura
  - Grupo sanguíneo
  - Sexo o género
  - Fecha de expedición
  - Lugar de expedición
- Almacena los datos en una base de datos MySQL.
- Devuelve advertencias si el documento no es válido o el texto es ilegible.
- Permite pruebas locales (no requiere GCP).

## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPO_PRIVADO.git
   cd TU_REPO_PRIVADO
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instala dependencias del sistema:**
   - Para PDFs: `poppler-utils`
   ```bash
   sudo apt update
   sudo apt install poppler-utils
   ```

5. **Configura el archivo `.env`:**
   Copia y edita según tus credenciales:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=usuario_db
   DB_PASSWORD=tu_password_segura
   DB_NAME=davinchi
   OPENAI_API_KEY=sk-xxxxxx
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_MAX_TOKENS=1200
   LOG_LEVEL=INFO
   ENABLE_CACHE=True
   CACHE_TTL=300
   ```

6. **Crea la base de datos y la tabla:**
   ```sql
   CREATE DATABASE davinchi;
   USE davinchi;
   CREATE TABLE documentos (
       id INT AUTO_INCREMENT PRIMARY KEY,
       tipo_documento VARCHAR(50),
       numero_documento VARCHAR(30),
       nombres VARCHAR(100),
       apellidos VARCHAR(100),
       fecha_nacimiento VARCHAR(20),
       lugar_nacimiento VARCHAR(100),
       estatura VARCHAR(20),
       grupo_sanguineo VARCHAR(10),
       sexo VARCHAR(10),
       fecha_expedicion VARCHAR(20),
       lugar_expedicion VARCHAR(100),
       texto_legible TEXT
   );
   ```

## Uso

1. **Inicia el servidor:**
   ```bash
   uvicorn app:app --reload
   ```

2. **Accede a la documentación interactiva:**
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. **Ejemplo de request (Postman o curl):**
   - Para PDF:
     ```json
     {
       "filename": "documento.pdf",
       "file_base64": "AQUI_TODO_EL_BASE64"
     }
     ```
   - Para imágenes (frente y respaldo):
     ```json
     {
       "filename": "documento.jpg",
       "files_base64": [
         "BASE64_FRENTE",
         "BASE64_RESPALDO"
       ]
     }
     ```

4. **Conversión de archivos a base64:**
   Usa el script conversor.py:
   ```bash
   python conversor.py archivo_entrada.ext archivo_salida.txt
   ```

## Notas
- El sistema permite PDFs de máximo 2 páginas.
- Los archivos originales se guardan en la carpeta uploads/.
- El endpoint devuelve advertencias si el documento no es válido o el texto es ilegible.
- Si tienes problemas con la extracción de campos, revisa la calidad del documento y el formato.



## Licencia
Proyecto privado para uso interno. 
