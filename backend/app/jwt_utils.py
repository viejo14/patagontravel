from datetime import datetime, timedelta       # Importamos utilidades para manejar fechas y tiempos (ahora, y sumas/restas de tiempo)
from jose import jwt, JWTError                 # Importamos funciones para crear/verificar JWT y el error que salta si algo va mal

# 🔐 Clave secreta para firmar/verificar los tokens.
# Debe estar en una variable de entorno en producción, nunca fija en el código.
SECRET_KEY = "tu_clave_secreta_super_segura"

# 📜 Algoritmo de firma del JWT (HS256 = HMAC con SHA-256, usa misma clave para firmar y verificar)
ALGORITHM = "HS256"

# ---------------------------------------------------------
def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    """
    Crea un token JWT a partir de un diccionario de datos (claims) y un tiempo de expiración.
    """
    to_encode = data.copy()                           # Copiamos el diccionario para no modificar el original
    expire = datetime.utcnow() + expires_delta        # Calculamos fecha/hora de expiración sumando el delta al tiempo actual
    to_encode.update({"exp": expire})                 # Añadimos la fecha de expiración al payload bajo la clave estándar 'exp'
    # Firmamos y codificamos el token con la clave secreta y el algoritmo elegido
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------------------------------------------
def verify_jwt_token(token: str) -> dict:
    """
    Decodifica y verifica un JWT.
    Devuelve el payload si es válido o None si es inválido/expirado.
    """
    try:
        # Intentamos decodificar el token usando la clave y algoritmo correctos
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload                                # Si pasa todas las verificaciones, devolvemos la data original
    except JWTError:
        return None                                   # Si hay error de firma, expiración o formato → None

# ---------------------------------------------------------
def create_password_reset_token(user_id: int) -> str:
    """
    Genera un token especial para recuperación de contraseña.
    Tiene un 'scope' específico y expira rápido (15 min).
    """
    data = {"sub": str(user_id), "scope": "password_reset"}  # 'sub' = subject (ID de usuario) y 'scope' define el propósito
    return create_jwt_token(data, timedelta(minutes=15))     # Creamos el JWT usando la función base

# ---------------------------------------------------------
def verify_password_reset_token(token: str):
    """
    Verifica que el token de reset sea válido, no esté expirado y tenga el scope correcto.
    Si todo está bien, devuelve el ID de usuario; si no, devuelve None.
    """
    payload = verify_jwt_token(token)                       # Reutilizamos la función genérica de verificación
    if payload and payload.get("scope") == "password_reset":# Comprobamos que el scope sea el esperado
        return payload.get("sub")                           # Devolvemos el ID de usuario
    return None                                             # Si falla cualquier verificación, devolvemos None