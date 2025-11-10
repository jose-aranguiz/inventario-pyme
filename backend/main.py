from fastapi import FastAPI

# Creamos la aplicación
app = FastAPI(
    title="API Inventario Pyme",
    description="Backend para control de inventario",
    version="0.1.0"
)

# Ruta de inicio (para probar que vive)
@app.get("/")
def read_root():
    return {"mensaje": "¡Hola! Tu backend está funcionando correctamente 🚀"}