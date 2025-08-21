from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "tu_clave_secreta_super_segura"
ALGORITHM = "HS256"

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)