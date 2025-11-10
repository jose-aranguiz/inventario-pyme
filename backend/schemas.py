from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Esquemas para Producto ---

# Datos base que compartimos al crear y leer
class ProductoBase(BaseModel):
    nombre: str
    codigo_sku: Optional[str] = None
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    stock_minimo: int = 5

# Lo que necesitamos recibir para crear un producto (todo lo base es suficiente)
class ProductoCreate(ProductoBase):
    pass

# Lo que devolveremos al frontend (incluye el ID y el stock actual, que no los creamos manualmente)
class Producto(ProductoBase):
    id: int
    stock_actual: int

    class Config:
        from_attributes = True # Esto permite a Pydantic leer directamente de los modelos de SQLAlchemy

# --- Esquemas para MovimientoStock ---

class MovimientoStockBase(BaseModel):
    tipo: str # "ENTRADA" o "SALIDA"
    cantidad: int
    motivo: Optional[str] = None

class MovimientoStockCreate(MovimientoStockBase):
    producto_id: int

class MovimientoStock(MovimientoStockBase):
    id: int
    fecha_hora: datetime
    
    class Config:
        from_attributes = True