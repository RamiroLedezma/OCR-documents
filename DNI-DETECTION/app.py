from flask import Flask, request, jsonify
from utils.openai_ocr import extract_info_from_base64
#from models.database import save_to_mysql
import base64
import os
from flask import render_template



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar_documento():
    data = request.get_json()

    base64_file = data.get("archivo_base64")
    if not base64_file:
        return jsonify({"error": "Archivo base64 es requerido"}), 400

    try:
        resultado = extract_info_from_base64(base64_file)
        #save_to_mysql(resultado)  # Guarda en base de datos
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
