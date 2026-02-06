from fastapi import FastAPI, Request
import sqlite3
import os

app = FastAPI()

# Ruta absoluta hacia tu USB
BASE_DIR = "/mnt/datos/hub_domotico"
DB_PATH = os.path.join(BASE_DIR, "sensores.db")

def init_db():
    # Verificamos si la USB está montada
    if not os.path.exists(BASE_DIR):
        print(f"CRÍTICO: No se encuentra la ruta {BASE_DIR}. Revisa la USB.")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Creamos una tabla simple para tus sensores
    cursor.execute('''CREATE TABLE IF NOT EXISTS lecturas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       sensor_name TEXT, 
                       valor REAL, 
                       fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print(f"Base de datos verificada en: {DB_PATH}")
    return True

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"mensaje": "Hub Domótico Activo", "ubicacion_db": DB_PATH}

@app.post("/update")
async def update_sensor(request: Request):
    data = await request.json()
    # data debe ser algo como: {"nombre": "sala", "valor": 24.5}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lecturas (sensor_name, valor) VALUES (?, ?)", 
                       (data['nombre'], data['valor']))
        conn.commit()
        conn.close()
        return {"status": "ok", "guardado_en": DB_PATH}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Iniciamos el servidor en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)   
