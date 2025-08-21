from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 📦 URL de conexión (SQLite local para desarrollo)
SQLALCHEMY_DATABASE_URL = "sqlite:///./patagontravel.db"

# 🔌 Crear motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 🧠 Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🧱 Base para modelos
Base = declarative_base()