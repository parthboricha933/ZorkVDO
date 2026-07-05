"""Video routes: /api/v1/videos/*."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUserId, get_video_service
from app.models.projects import VideoPublic
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=VideoPublic, status_code=201)
async def upload_video(
    user_id: CurrentUserId,
    file: UploadFile = File(...),
    kind: str = Form("source"),
    svc: VideoService = Depends(get_video_service),
) -> VideoPublic:
    """Direct upload — file streamed through the API.

    For very large files (>100MB) prefer the presigned-URL flow once
    the S3 backend is configured; this endpoint is fine for dev/small clips.
    """
    stream = await file.read()
    return await svc.upload(
        owner_id=user_id,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(stream),
        kind=kind,
        stream=stream,
    )


@router.get("", response_model=list[VideoPublic])
async def list_videos(
    user_id: CurrentUserId,
    kind: str | None = Query(None, pattern="^(source|user_clip|output)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: VideoService = Depends(get_video_service),
) -> list[VideoPublic]:
    return await svc.list(user_id, kind=kind, limit=limit, offset=offset)


@router.get("/{video_id}", response_model=VideoPublic)
async def get_video(
    video_id: str,
    user_id: CurrentUserId,
    svc: VideoService = Depends(get_video_service),
) -> VideoPublic:
    return await svc.get(user_id, video_id)


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    user_id: CurrentUserId,
    svc: VideoService = Depends(get_video_service),
) -> StreamingResponse:
    data, video = await svc.get_bytes(user_id, video_id)

    import io

    def iter_data():
        yield data

    return StreamingResponse(
        iter_data(),
        media_type=video.content_type,
        headers={"Content-Disposition": f'attachment; filename="{video.filename}"'},
    )


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    user_id: CurrentUserId,
    svc: VideoService = Depends(get_video_service),
) -> dict:
    return {"deleted": await svc.delete(user_id, video_id)}
