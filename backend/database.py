from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Usaremos SQLite por ahora. El archivo se creará automáticamente como 'inventario.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./inventario.db"

# Creamos el motor de conexión.
# connect_args={"check_same_thread": False} es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creamos una clase "SessionLocal". Cada instancia de esta clase será una sesión de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nuestros modelos. Todos los modelos heredarán de aquí.
Base = declarative_base()

# Función de utilidad para obtener la sesión de DB en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()