from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserRegister


class AuthService:

    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> tuple[User, str]:
        """
        Registra un nuevo usuario.
        Retorna (user, token).
        Lanza 400 si el email ya existe.
        """
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una cuenta con ese email",
            )

        user = User(
            nombres=data.nombres,
            apellidos=data.apellidos,
            email=data.email,
            password_hash=hash_password(data.password),
            provider="local",
        )
        db.add(user)
        await db.flush()

        token = create_access_token({"sub": str(user.id)})
        return user, token

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> tuple[User, str]:
        """
        Verifica credenciales y retorna (user, token).
        Lanza 401 si las credenciales son incorrectas.
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada",
            )

        token = create_access_token({"sub": str(user.id)})
        return user, token

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> User:
        """Retorna un usuario por ID o lanza 404."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user