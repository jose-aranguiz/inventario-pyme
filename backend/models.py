from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    codigo_sku = Column(String, unique=True, index=True, nullable=True)
    precio_costo = Column(Float, default=0.0)
    precio_venta = Column(Float, default=0.0)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5) # Alerta si baja de 5 unidades

    # Relación con movimientos (para poder acceder a ellos fácilmente desde un producto)
    movimientos = relationship("MovimientoStock", back_populates="producto")

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String, nullable=False) # "ENTRADA" o "SALIDA"
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String, nullable=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())

    # Relación inversa
    producto = relationship("Producto", back_populates="movimientos")