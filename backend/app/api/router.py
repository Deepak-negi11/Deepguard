from fastapi import APIRouter

from app.api.v1 import auth, history, results, verify

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(verify.router, prefix="/verify", tags=["verify"])
router.include_router(results.router, prefix="/results", tags=["results"])
router.include_router(history.router, prefix="/history", tags=["history"])
