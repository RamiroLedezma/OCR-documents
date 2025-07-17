import base64
import sys
import os
import uuid

def convertir_a_base64_y_guardar(input_path: str, output_path: str):
    with open(input_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    with open(output_path, "w") as f:
        f.write(encoded)
    print(f"Base64 guardado en {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python conversor.py archivo_entrada.ext archivo_salida.txt")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convertir_a_base64_y_guardar(input_file, output_file)