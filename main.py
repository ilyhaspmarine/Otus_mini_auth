from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from prometheus_fastapi_instrumentator import Instrumentator

import auth_utils
from auth_db_schema import Auth as AuthSchema
from auth_db import _get_db
from auth_models import TokenInfo, AuthCreate, AuthBase

# import uvicorn

app = FastAPI(title="Auth Service", version="1.0.0")

@app.get('/health', summary='HealthCheck EndPoint', tags=['Health Check'])
def healthcheck():
    return {'status': 'OK'}

@app.post('/login', response_model=TokenInfo, status_code=status.HTTP_200_OK)
async def auth_user_issue_token(
    user: AuthSchema = Depends(auth_utils._validate_auth_user)
):
    jwt_payload = {
        "sub": user.username,
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="bearer",
    )

@app.get('/validate', status_code=status.HTTP_200_OK)
async def auth_user_validate_token(
    payload: dict = Depends(auth_utils._get_current_token_payload)
):
    return {
        "username": payload.get("sub"),
        "iat": payload.get("iat")
    }

@app.post('/register', response_model=AuthBase, status_code=status.HTTP_201_CREATED)
async def auth_user_create_new(
    user: AuthCreate, 
    db = Depends(_get_db)
):
    db_user = AuthSchema(
        username = user.username,
        hashed_pswd = auth_utils.hash_password(user.password)
    )
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    return AuthBase(
        username = db_user.username
    )

# Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)