from datetime import timedelta
from .jwt_utils import create_jwt_token

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_tokens(data: dict):
    access_token = create_jwt_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return access_token, refresh_token