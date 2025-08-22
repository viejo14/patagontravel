from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models, database
from .jwt_utils import SECRET_KEY, ALGORITHM

router_users = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router_users.get("/registered")
def list_registered_users(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Filtramos solo usuarios con rol "user"
    users = db.query(models.User).filter(models.User.role == "user").all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]