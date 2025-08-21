from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 📂 Ruta absoluta al archivo patagontravel.db en la carpeta backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "patagontravel.db")

# 📦 URL de conexión (SQLite local para desarrollo)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 🔌 Crear motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 🧠 Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🧱 Base para modelos
Base = declarative_base()