from fastapi import APIRouter, Depends

from app.api.v1 import auth, gradcam, history, results, system, verify
from app.csrf import enforce_csrf

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(verify.router, prefix="/verify", tags=["verify"], dependencies=[Depends(enforce_csrf)])
router.include_router(results.router, prefix="/results", tags=["results"])
router.include_router(history.router, prefix="/history", tags=["history"])
router.include_router(system.router, prefix="/system", tags=["system"])
router.include_router(gradcam.router, prefix="/gradcam", tags=["gradcam"])
