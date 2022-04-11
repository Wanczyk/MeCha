from fastapi import APIRouter
from src.api.v1.user import router as v1_user

router_v1 = APIRouter(prefix='/v1', tags=["v1"],)

router_v1.include_router(v1_user)
