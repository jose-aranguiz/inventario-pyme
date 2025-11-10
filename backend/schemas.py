from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Esquemas Base ---
class ProductoBase(BaseModel):
    nombre: str
    codigo_sku: Optional[str] = None
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    stock_minimo: int = 5

class MovimientoStockBase(BaseModel):
    tipo: str
    cantidad: int
    motivo: Optional[str] = None

# --- Esquemas de Creación (Input) ---
class ProductoCreate(ProductoBase):
    pass

class MovimientoStockCreate(MovimientoStockBase):
    producto_id: int

# --- Esquemas de Lectura (Output) ---

# Primero definimos Producto básico para usarlo dentro de Movimiento
class Producto(ProductoBase):
    id: int
    stock_actual: int
    class Config:
        from_attributes = True

# Ahora Movimiento puede usar Producto
class MovimientoStock(MovimientoStockBase):
    id: int
    producto_id: int
    fecha_hora: datetime
    # ¡Magia! Esto incluirá automáticamente los datos del producto relacionado
    producto: Optional[Producto] = None 

    class Config:
        from_attributes = True