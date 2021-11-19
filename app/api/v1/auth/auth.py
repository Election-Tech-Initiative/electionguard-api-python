from typing import Any, List, Optional

from datetime import datetime, timedelta

from fastapi import (
    params,
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError

from app.api.v1.models.user import UserScope
from app.core import Settings
from app.core.user import get_user_info

from ..models import Token, TokenData

from ....core import AuthenticationContext

from ..tags import AUTHORIZE

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        UserScope.admin: "The admin role can execute administrative functions.",
        UserScope.auditor: "The auditor role is a readonly role that can observe the election",
        UserScope.guardian: "The guardian role can excute guardian functions.",
        UserScope.voter: "The voter role can execute voting functions such as encrypt ballot.",
    },
)


class ScopedTo(params.Depends):
    """Define a dependency on particular scope."""

    def __init__(self, scopes: List[UserScope]) -> None:
        super().__init__(self.__call__)
        self._scopes = scopes

    def __call__(
        self,
        request: Request,
        settings: Settings = Settings(),
        token: str = Security(oauth2_scheme),
    ) -> TokenData:
        """Check scopes and return the current user."""
        data = validate_access_token(settings, token)
        validate_access_token_authorization(data, self._scopes)
        return data


def validate_access_token_authorization(
    token_data: TokenData, scopes: List[UserScope]
) -> None:
    """Validate that the access token is authorized to the requested resource."""
    if any(scopes):
        scope_str = ",".join(scopes)
        authenticate_value = f'Bearer scope="{scope_str}"'
    else:
        authenticate_value = "Bearer"
    for scope in scopes:
        if scope in token_data.scopes:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": authenticate_value},
    )


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    settings: Settings = Settings(),
) -> Any:
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )
    return encoded_jwt


def validate_access_token(
    settings: Settings = Settings(), token: str = Depends(oauth2_scheme)
) -> TokenData:
    """validate the token contains a username and scopes"""
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_scopes = payload.get("scopes")
        token_data = TokenData(username=username, scopes=token_scopes)
    except (JWTError, ValidationError) as internal_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credential scopes",
            headers={"WWW-Authenticate": "Bearer"},
        ) from internal_error
    return token_data


@router.post("/login", response_model=Token, tags=[AUTHORIZE])
async def login_for_access_token(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """Log in using the provided username and password."""
    authenticated = AuthenticationContext(
        request.app.state.settings
    ).authenticate_credential(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # get the database cached user info
    user_info = get_user_info(form_data.username, request.app.state.settings)
    access_token_expires = timedelta(
        minutes=request.app.state.settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": form_data.username, "scopes": user_info.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


# TODO: add refresh support
