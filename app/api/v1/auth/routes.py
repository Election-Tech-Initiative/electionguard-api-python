from fastapi import APIRouter
from . import auth
from . import user

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(user.router, prefix="/user")
