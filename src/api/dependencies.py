import typing
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import UUID4

from api.models import InterServiceData, JwtUserData
from config import settings
from database.manager import ObjectDoesntExist
from database.models import ProjectDB, ProjectManager, get_project_manager


class UnauthenticatedException(Exception):
    def __init__(self, message: Optional[str] = None):
        self.message = message or None
        self.status = 401
        super().__init__(self.message)


http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    authorization: typing.Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> JwtUserData:
    if authorization is None:
        raise UnauthenticatedException()
    try:
        payload: dict = jwt.decode(
            authorization.credentials,
            settings.jwt_secret,
            algorithms=jwt.ALGORITHMS.HS256,
            audience="fastapi-users:auth",
        )
    except ExpiredSignatureError:
        print("JWT token expired")
        raise UnauthenticatedException("Token expired")
    except JWTError:
        print("Invalid JWT token")
        raise UnauthenticatedException("Invalid bearer token")
    return JwtUserData(user_id=payload.get("user_id"))


async def get_current_inter_service_data(
    authorization: typing.Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> InterServiceData:
    if authorization is None:
        raise UnauthenticatedException()
    try:
        payload: dict = jwt.decode(
            authorization.credentials,
            settings.jwt_secret,
            algorithms=jwt.ALGORITHMS.HS256,
            audience="fastapi-users:auth",
        )
    except ExpiredSignatureError:
        print("JWT token expired")
        raise UnauthenticatedException("Token expired")
    except JWTError:
        print("Invalid JWT token")
        raise UnauthenticatedException("Invalid bearer token")
    return InterServiceData(
        user_id=payload.get("user_id"), project_id=payload.get("project_id")
    )


async def get_project_or_404(
    project_id: UUID4,
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_manager: ProjectManager = Depends(get_project_manager),
) -> ProjectDB:
    try:
        return await project_manager.get(project_id, jwt_user_data.user_id)
    except ObjectDoesntExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
