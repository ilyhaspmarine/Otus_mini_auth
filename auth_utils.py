from datetime import datetime, timedelta
import bcrypt
import jwt
from auth_config import settings
from auth_db import _get_db
from fastapi import Depends, HTTPException, status
from auth_db_schema import Auth as AuthSchema
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

http_bearer = HTTPBearer()

def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    to_encode = payload
    now = datetime.utcnow()
    to_encode.update(
        exp = now +  timedelta(minutes=expire_minutes),
        iat = now
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded

def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )

async def get_user_by_name(
        username: str,
        db: AsyncSession
) -> AuthSchema:
    result = await db.execute(select(AuthSchema).filter(AuthSchema.username == username))
    return result.scalar_one_or_none()

async def _validate_auth_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db=Depends(_get_db)
) -> AuthSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    user = await get_user_by_name(form_data.username, db)
    if not user:
        raise unauthed_exc
    
    if not validate_password(password=form_data.password, hashed_password=user.hashed_pswd):
        raise unauthed_exc
    
    return user

async def _process_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db=Depends(_get_db)
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error",
        )
    
    user = await get_user_by_name(payload.get("sub"), db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error",
        )

    return payload

