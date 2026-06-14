from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


# ─── Hash de contraseñas ────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT Tokens ─────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict) -> str:
    """
    Genera un JWT con los datos del usuario.
    Expira según ACCESS_TOKEN_EXPIRE_MINUTES del .env
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza HTTPException 401 si el token es inválido o expiró.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency para rutas protegidas.
    Uso:
        @router.get("/perfil")
        async def perfil(user_id: str = Depends(get_current_user_id)):
            ...
    """
    payload = decode_access_token(token)
    return payload.get("sub")


def get_optional_user_id(token: str = Depends(oauth2_scheme)) -> str | None:
    """
    Dependency para rutas que funcionan con o sin login.
    Si el token es inválido simplemente retorna None en vez de lanzar error.
    Uso: endpoints que dan más funciones a logueados pero funcionan como invitado.
    """
    try:
        payload = decode_access_token(token)
        return payload.get("sub")
    except HTTPException:
        return None