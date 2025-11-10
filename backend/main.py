from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTACIÓN NUEVA
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db
import models, schemas

# Crear tablas al inicio
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Inventario Pyme",
    description="Backend para control de inventario",
    version="0.1.0"
)

# --- CONFIGURACIÓN DE CORS (NUEVO BLOQUE) ---
# Esto permite que tu frontend en el puerto 9000 hable con este backend en el puerto 8000
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Permite todos los headers
)
# --------------------------------------------

# --- RUTAS DE PRODUCTOS ---

@app.post("/productos/", response_model=schemas.Producto)
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    # Verificamos si ya existe un producto con ese SKU (si se proporcionó SKU)
    if producto.codigo_sku:
        db_producto = db.query(models.Producto).filter(models.Producto.codigo_sku == producto.codigo_sku).first()
        if db_producto:
            raise HTTPException(status_code=400, detail="Ya existe un producto con este código SKU")

    # Creamos el nuevo producto
    nuevo_producto = models.Producto(**producto.dict())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto) # Recargamos para obtener el ID generado
    return nuevo_producto

@app.get("/productos/", response_model=List[schemas.Producto])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = db.query(models.Producto).offset(skip).limit(limit).all()
    return productos

@app.get("/productos/{producto_id}", response_model=schemas.Producto)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# --- RUTA DE PRUEBA ---
@app.get("/")
def read_root():
    return {"mensaje": "API de Inventario funcionando correctamente 🚀"}

# --- RUTAS DE MOVIMIENTOS DE STOCK ---

@app.post("/movimientos/", response_model=schemas.MovimientoStock)
def crear_movimiento(movimiento: schemas.MovimientoStockCreate, db: Session = Depends(get_db)):
    # 1. Buscamos el producto afectado
    db_producto = db.query(models.Producto).filter(models.Producto.id == movimiento.producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Calculamos el nuevo stock según el tipo de movimiento
    if movimiento.tipo == "ENTRADA":
        db_producto.stock_actual += movimiento.cantidad
    elif movimiento.tipo == "SALIDA":
        # Opcional: Verificar si hay stock suficiente antes de restar
        if db_producto.stock_actual < movimiento.cantidad:
             raise HTTPException(status_code=400, detail="No hay stock suficiente para esta salida")
        db_producto.stock_actual -= movimiento.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido. Debe ser ENTRADA o SALIDA")

    # 3. Creamos el registro del movimiento
    nuevo_movimiento = models.MovimientoStock(**movimiento.dict())
    
    # 4. Guardamos AMBOS cambios (el movimiento nuevo y la actualización del producto)
    db.add(nuevo_movimiento)
    # No necesitamos hacer db.add(db_producto) porque SQLAlchemy ya sabe que lo modificamos
    db.commit()
    db.refresh(nuevo_movimiento)
    
    return nuevo_movimiento