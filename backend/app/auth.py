import uuid
from fastapi import APIRouter, Depends, HTTPException, Form, Header
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from . import models, database
from .jwt_utils import (
    SECRET_KEY,
    ALGORITHM,
    create_password_reset_token,
    verify_password_reset_token
)  # Importamos lo necesario para JWT y recuperación

# 📌 Inicializamos router con prefijo /auth
router = APIRouter(prefix="/auth", tags=["auth"])

# Configuración de bcrypt para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========================
# 📦 Modelos Pydantic
# ========================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None
    role: str
    username: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: str  # Email o username, según tu modelo

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# ========================
# 🛠 Funciones de utilidad
# ========================

def hash_password(password: str) -> str:
    """Genera un hash seguro para la contraseña."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña en texto plano coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_long_lived_token(data: dict, days: int = 365) -> str:
    """Crea un token JWT con expiración larga."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict | None:
    """Verifica y decodifica un token JWT, devuelve payload o None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def require_non_guest(authorization: str = Header(...)):
    """Dependencia que permite acceso solo a usuarios que no sean 'guest'."""
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("role") == "guest":
        raise HTTPException(status_code=403, detail="No permitido para invitados")
    return payload

def get_db():
    """Provee conexión a la base de datos y la cierra al final."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================
# 🔑 Endpoints de autenticación
# ========================

@router.post("/register", response_model=TokenResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    username = username.strip().lower()

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
        "refresh_token": None,
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
    """Endpoint protegido para subir archivos, solo usuarios no guest."""
    return {"message": "Archivo subido con éxito", "usuario": user.get("sub")}

@router.post("/guest", response_model=TokenResponse)
def guest_login(db: Session = Depends(get_db)):
    """Genera un usuario invitado y devuelve su token."""
    guest_id = str(uuid.uuid4())[:8]
    guest_username = f"Invitado-{guest_id}"

    guest_user = models.User(username=guest_username, role="guest")
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    access_token = create_long_lived_token({"sub": guest_username, "role": "guest"})

    return {
        "access_token": access_token,
        "refresh_token": None,
        "role": "guest",
        "username": guest_username,
        "token_type": "bearer"
    }

# ========================
# 🔄 Recuperación de contraseña
# ========================

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Busca usuario por email/username y genera un token de recuperación.
    Por ahora el link se imprime en consola; luego puede enviarse por email.
    """
    user = db.query(models.User).filter(models.User.username == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    token = create_password_reset_token(user.id)
    print(f"🔗 Enlace de recuperación: https://tusitio.com/reset-password?token={token}")
    
    return {"message": "Si el usuario existe, se enviará un enlace para restablecer la contraseña"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Valida el token de recuperación, busca el usuario y actualiza su contraseña.
    """
    user_id = verify_password_reset_token(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada con éxito"}