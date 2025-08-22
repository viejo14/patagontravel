from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# Importamos módulos internos
from . import auth, models, database, users  # 👈 aquí agregamos "users"

# 🔧 Inicialización de la app
app = FastAPI(title="PatagonTravel API", version="0.0.1")

# 🗃️ Crear tablas en la base de datos
models.Base.metadata.create_all(bind=database.engine)

# 📦 Incluir rutas del módulo auth (todas las rutas que empiezan con /auth)
app.include_router(auth.router)

# 📦 Incluir rutas del módulo users (ej: /users/registered)
app.include_router(users.router_users)  # 👈 integración del nuevo router

# 🩺 Ruta de verificación básica
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 🧠 Dependencia para obtener sesión de base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔑 Endpoint de login adicional (usa la lógica de auth.py pero con OAuth2PasswordRequestForm)
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# 🛡️ Ruta protegida que requiere un token válido
@app.get("/protected")
def protected_route(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]  # Extrae el token del header "Bearer <token>"
    except IndexError:
        raise HTTPException(status_code=400, detail="Formato de autorización inválido")

    username = auth.verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {"message": f"Hola {username}, accediste a una ruta protegida"}

# 🚫 Eliminado el /auth/me aquí — se usa el de auth.py que ya maneja invitados y usuarios

# 🌐 Middleware CORS para permitir conexión con el frontend en localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # origen del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)