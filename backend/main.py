from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
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

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS DE PRODUCTOS ---

@app.post("/productos/", response_model=schemas.Producto)
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    if producto.codigo_sku:
        db_producto = db.query(models.Producto).filter(models.Producto.codigo_sku == producto.codigo_sku).first()
        if db_producto:
            raise HTTPException(status_code=400, detail="Ya existe un producto con este código SKU")

    nuevo_producto = models.Producto(**producto.dict())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
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

@app.put("/productos/{producto_id}", response_model=schemas.Producto)
def actualizar_producto(producto_id: int, producto_actualizado: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificamos si el nuevo SKU ya existe en OTRO producto (si es que cambió el SKU)
    if producto_actualizado.codigo_sku and producto_actualizado.codigo_sku != db_producto.codigo_sku:
         sku_existe = db.query(models.Producto).filter(models.Producto.codigo_sku == producto_actualizado.codigo_sku).first()
         if sku_existe:
             raise HTTPException(status_code=400, detail="Ya existe otro producto con este nuevo código SKU")

    # Actualizamos los campos
    for key, value in producto_actualizado.dict().items():
        setattr(db_producto, key, value)

    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar si tiene movimientos antes de borrar (opcional, pero recomendado para integridad)
    # Si permitimos borrar productos con movimientos, el historial podría quedar "huerfano".
    # Por ahora, lo permitiremos para simplificar, pero en un sistema real lo bloquearíamos.

    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}

# --- RUTAS DE MOVIMIENTOS ---

@app.post("/movimientos/", response_model=schemas.MovimientoStock)
def crear_movimiento(movimiento: schemas.MovimientoStockCreate, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == movimiento.producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if movimiento.tipo == "ENTRADA":
        db_producto.stock_actual += movimiento.cantidad
    elif movimiento.tipo == "SALIDA":
        if db_producto.stock_actual < movimiento.cantidad:
             raise HTTPException(status_code=400, detail="No hay stock suficiente para esta salida")
        db_producto.stock_actual -= movimiento.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido")

    nuevo_movimiento = models.MovimientoStock(**movimiento.dict())
    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)
    return nuevo_movimiento

@app.get("/movimientos/", response_model=List[schemas.MovimientoStock])
def listar_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movimientos = db.query(models.MovimientoStock)\
        .options(joinedload(models.MovimientoStock.producto))\
        .order_by(models.MovimientoStock.fecha_hora.desc())\
        .offset(skip).limit(limit).all()
    return movimientos

# --- RUTA BASE ---
@app.get("/")
def read_root():
    return {"mensaje": "API de Inventario funcionando correctamente 🚀"}