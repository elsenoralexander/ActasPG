import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

def test_connection():
    # Try to load credentials
    # 1. Look for .streamlit/secrets.toml (simulated here by checking for a json file if secrets not available)
    # Since this script runs outside streamlit, we need to point to a json file
    
    path_to_key = "firebase_key.json"
    
    # Auto-detect if there's a file with the typical Firebase name
    if not os.path.exists(path_to_key):
        files = [f for f in os.listdir(".") if f.endswith(".json") and ("firebase-adminsdk" in f or f.startswith("actas-"))]
        if files:
            path_to_key = files[0]
            print(f"🧐 Detectado posible archivo de clave: {path_to_key}")
    
    if not os.path.exists(path_to_key):
        print(f"❌ Error: No se encontró el archivo JSON de Firebase.")
        print("Para probar la conexión:")
        print(f"1. Mueve el archivo que descargaste a esta carpeta: {os.getcwd()}")
        print("2. Asegúrate de que termine en .json")
        return

    try:
        cred = credentials.Certificate(path_to_key)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("✅ Conexión exitosa a Firebase Firestore.")
        
        # Test write
        doc_ref = db.collection("test").document("check")
        doc_ref.set({"status": "ok", "message": "Conexión probada desde el Agente"})
        print("✅ Escritura de prueba exitosa.")
        
        # Test read
        doc = doc_ref.get()
        if doc.exists:
            print(f"✅ Lectura de prueba exitosa: {doc.to_dict()}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    test_connection()
