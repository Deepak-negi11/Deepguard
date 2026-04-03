"""
Grad-CAM heatmap file serving endpoint.
Serves PNG heatmaps generated during image analysis from /uploads/gradcam/.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

router = APIRouter()

GRADCAM_DIR = Path("/app/uploads/gradcam")


@router.get("/{filename}", response_class=FileResponse)
def serve_gradcam(filename: str) -> FileResponse:
    # Sanitise — only allow plain filenames, no path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    file_path = GRADCAM_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heatmap not found")

    return FileResponse(str(file_path), media_type="image/png")
