import uuid
from fastapi import APIRouter, Depends, HTTPException, Form, Header
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from . import models, database
from .jwt_utils import SECRET_KEY, ALGORITHM  # evitar import circular

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========================
# Modelos Pydantic
# ========================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None
    role: str
    username: str
    token_type: str

# ========================
# Utilidades
# ========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_long_lived_token(data: dict, days: int = 365) -> str:
    """Crea un token con expiración muy larga."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def require_non_guest(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("role") == "guest":
        raise HTTPException(status_code=403, detail="No permitido para usuarios invitados")
    return payload

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================
# Endpoints
# ========================

@router.post("/register", response_model=TokenResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # normalizar nombre de usuario
    username = username.strip().lower()

    # evitar duplicados
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = hash_password(password)
    new_user = models.User(
        username=username,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # token inmediato tras registro
    access_token = create_long_lived_token({"sub": new_user.username, "role": new_user.role})

    return {
        "access_token": access_token,
        "refresh_token": None,
        "role": new_user.role,
        "username": new_user.username,
        "token_type": "bearer"
    }


@router.post("/login", response_model=TokenResponse)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_long_lived_token({"sub": user.username, "role": "user"})
    return {
        "access_token": access_token,
        "refresh_token": None,  # No necesitamos refresh
        "role": "user",
        "username": user.username,
        "token_type": "bearer"
    }

@router.get("/me")
def read_users_me(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("role") == "guest":
        return {"username": payload.get("sub"), "role": "guest"}

    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"username": user.username, "role": "user"}

@router.post("/upload")
def upload_file(user=Depends(require_non_guest)):
    return {"message": "Archivo subido con éxito", "usuario": user.get("sub")}

@router.post("/guest", response_model=TokenResponse)
def guest_login(db: Session = Depends(get_db)):
    # Generar username único
    guest_id = str(uuid.uuid4())[:8]
    guest_username = f"Invitado-{guest_id}"

    # Crear usuario en DB con rol guest
    guest_user = models.User(username=guest_username, role="guest")
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    # Crear token
    access_token = create_long_lived_token({"sub": guest_username, "role": "guest"})

    return {
        "access_token": access_token,
        "refresh_token": None,
        "role": "guest",
        "username": guest_username,
        "token_type": "bearer"
    }