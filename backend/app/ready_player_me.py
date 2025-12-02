"""A small FastAPI router that integrates with Ready Player Me (RPM) Avatar REST API.

Endpoints:
- POST /rpm-from-image-url {"image_url": "..."}
    Create an avatar from a public image URL, poll until ready, download the GLB and return it.

- POST /rpm-from-upload (multipart form field "file")
    Accept an uploaded image file. If IMGBB_API_KEY is provided it will upload the image to imgbb and use that public URL
    to call RPM. Otherwise it will return an error instructing to either provide IMGBB_API_KEY or call /rpm-from-image-url
    with a publicly hosted image URL.

- GET /rpm-health
    Simple health check and config report.

Notes:
- The exact Ready Player Me API responses can change; this router attempts to be flexible and check multiple possible
  response fields for avatar id / glb URL. If the exact endpoint/field names for the RPM API you are using differ,
  adjust the RPM_CREATE_PATH and the response parsing logic accordingly.
- Environment variables used:
  READY_PLAYER_ME_API_URL (required) — base API URL, e.g. https://api.readyplayer.me
  READY_PLAYER_ME_API_KEY (optional) — if RPM requires a Bearer token
  IMGBB_API_KEY (optional) — if you want the upload-from-file helper to host images for RPM via imgbb.com

"""

import os
import asyncio
import tempfile
import shutil
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

router = APIRouter()

READY_PLAYER_ME_API_URL = os.getenv("READY_PLAYER_ME_API_URL", "").rstrip('/')
READY_PLAYER_ME_API_KEY = os.getenv("READY_PLAYER_ME_API_KEY", "")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")

# Default paths — these may need to be adjusted depending on RPM's current API surface.
RPM_CREATE_PATH = "/v1/avatars"  # POST to create an avatar job (query params may be supported)
RPM_GET_AVATAR_PATH = "/v1/avatars/{id}"

if not READY_PLAYER_ME_API_URL:
    # Router will still import, but endpoints will error with clear message at runtime if not configured.
    pass

async def _upload_to_imgbb(image_bytes: bytes) -> str:
    """Upload bytes to imgbb and return a public image URL.
    Requires IMGBB_API_KEY in env. See https://api.imgbb.com/ for details.
    """
    if not IMGBB_API_KEY:
        raise RuntimeError("IMGBB_API_KEY is not configured")

    url = "https://api.imgbb.com/1/upload"
    data = {"key": IMGBB_API_KEY}
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"image": image_bytes}
        resp = await client.post(url, data=data, files=files)
        resp.raise_for_status()
        j = resp.json()
        # imgbb returns data.url for the non-base64 image: check structure
        # Example: {"data": {"url": "https://..."}, "success": true}
        data_obj = j.get("data") or {}
        img_url = data_obj.get("url") or data_obj.get("display_url")
        if not img_url:
            raise RuntimeError(f"imgbb did not return an image url: {j}")
        return img_url

async def _rpm_create_from_image_url(image_url: str) -> dict:
    if not READY_PLAYER_ME_API_URL:
        raise RuntimeError("READY_PLAYER_ME_API_URL is not configured")

    headers = {}
    if READY_PLAYER_ME_API_KEY:
        headers["Authorization"] = f"Bearer {READY_PLAYER_ME_API_KEY}"

    payload = {"imageUrl": image_url}
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try POST to create avatar job. Some RPM endpoints accept query param platform=web — include common variants.
        resp = await client.post(f"{READY_PLAYER_ME_API_URL}{RPM_CREATE_PATH}?platform=web", json=payload, headers=headers)
        if resp.status_code >= 400:
            # fallback without queryparam
            resp = await client.post(f"{READY_PLAYER_ME_API_URL}{RPM_CREATE_PATH}", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def _rpm_get_avatar_info(avatar_id: str) -> dict:
    headers = {}
    if READY_PLAYER_ME_API_KEY:
        headers["Authorization"] = f"Bearer {READY_PLAYER_ME_API_KEY}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{READY_PLAYER_ME_API_URL}{RPM_GET_AVATAR_PATH.format(id=avatar_id)}", headers=headers)
        resp.raise_for_status()
        return resp.json()

async def _extract_avatar_id(create_resp: dict) -> Optional[str]:
    # Try multiple common keys that RPM might return
    if not create_resp:
        return None
    for key in ("id", "avatar_id", "data", "result"):
        val = create_resp.get(key) if isinstance(create_resp, dict) else None
        if isinstance(val, str) and val:
            return val
        if isinstance(val, dict):
            # try nested id
            for nested_key in ("id", "avatar_id"):
                if nested_key in val and isinstance(val[nested_key], str):
                    return val[nested_key]
    # Some endpoints return the final URL directly (not an id)
    for possible_url_key in ("glb_url", "avatar_url", "url", "gltf", "gltf_url"):
        if possible_url_key in create_resp and isinstance(create_resp[possible_url_key], str):
            # We can return the URL in place of an id by using a special marker:
            return f"__url__:{create_resp[possible_url_key]}"
    return None

async def _find_glb_url_from_info(info: dict) -> Optional[str]:
    # Try multiple known fields/paths that may contain the glb/gltf url
    if not info:
        return None
    # direct keys
    for k in ("glb_url", "gltf_url", "avatar_url", "url", "result", "download_url"):
        v = info.get(k) if isinstance(info, dict) else None
        if isinstance(v, str) and v.endswith(".glb"):
            return v
        if isinstance(v, dict):
            # nested
            for subk in ("glb", "gltf", "url", "download_url"):
                subv = v.get(subk)
                if isinstance(subv, str) and subv.endswith(".glb"):
                    return subv
    # nested structures: data -> urls -> glb
    data = info.get("data") or {}
    if isinstance(data, dict):
        urls = data.get("urls") or data.get("result") or {}
        if isinstance(urls, dict):
            for candidate in ("glb", "glb_url", "gltf", "gltf_url", "avatar_url", "url"):
                u = urls.get(candidate)
                if isinstance(u, str) and u.endswith(".glb"):
                    return u
    # In some cases RPM returns a model URL that ends with .gltf or no extension; accept gltf too
    # look for any string containing '/avatars' or '/models' that looks like an asset
    def find_url(d):
        if isinstance(d, dict):
            for v in d.values():
                u = find_url(v)
                if u:
                    return u
        elif isinstance(d, list):
            for item in d:
                u = find_url(item)
                if u:
                    return u
        elif isinstance(d, str):
            if d.endswith(".glb") or d.endswith(".gltf") or "/avatar/" in d or "/avatars/" in d or "/models/" in d:
                return d
        return None
    return find_url(info)

@router.post("/rpm-from-image-url")
async def rpm_from_image_url(image_url: str):
    """Create an RPM avatar from a public image URL and return the generated GLB bytes.

    Flow:
      - POST create job to RPM with image_url
      - Extract job id (or possibly a direct glb URL)
      - Poll for completion and extract final GLB URL
      - Download GLB and stream back to caller
    """
    if not image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    try:
        create_resp = await _rpm_create_from_image_url(image_url)
        avatar_id = await _extract_avatar_id(create_resp)
        if not avatar_id:
            raise RuntimeError(f"Unexpected create response: {create_resp}")

        # If avatar_id is actually a URL marker, short-circuit
        if isinstance(avatar_id, str) and avatar_id.startswith("__url__:"):
            glb_url = avatar_id.split("__url__:", 1)[1]
        else:
            # poll until ready
            glb_url = None
            # Poll loop
            start = asyncio.get_event_loop().time()
            timeout = 120.0
            while True:
                info = await _rpm_get_avatar_info(avatar_id)
                # Try to extract glb url
                glb_url = await _find_glb_url_from_info(info)
                status = None
                if isinstance(info, dict):
                    status = info.get("status") or info.get("processingStatus") or (info.get("data") or {}).get("status")
                if glb_url:
                    break
                if status and str(status).lower() in ("failed", "error"):
                    raise RuntimeError(f"Avatar generation failed: {info}")
                if asyncio.get_event_loop().time() - start > timeout:
                    raise RuntimeError(f"Timed out waiting for RPM avatar. Last info: {info}")
                await asyncio.sleep(1.5)

        # Download GLB and stream back
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.get(glb_url)
            r.raise_for_status()
            tmpdir = tempfile.mkdtemp(prefix="rpm_")
            out_path = tmpdir + "/avatar.glb"
            with open(out_path, "wb") as f:
                f.write(r.content)

            async def file_iter():
                try:
                    with open(out_path, "rb") as fh:
                        while True:
                            chunk = fh.read(8192)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    shutil.rmtree(tmpdir, ignore_errors=True)

            return StreamingResponse(file_iter(), media_type="model/gltf-binary",
                                     headers={"Content-Disposition": 'attachment; filename="avatar.glb"'})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rpm-from-upload")
async def rpm_from_upload(file: UploadFile = File(...)):
    """Accept an uploaded image file and create an RPM avatar.

    If IMGBB_API_KEY is configured the file will be uploaded to imgbb to obtain a public URL. Otherwise
    the endpoint will return 400 and ask the caller to use /rpm-from-image-url with a hosted image URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be an image")
    if not IMGBB_API_KEY:
        raise HTTPException(status_code=400, detail="IMGBB_API_KEY not configured. Either provide IMGBB_API_KEY or call /rpm-from-image-url with a public image URL.")
    try:
        contents = await file.read()
        image_url = await _upload_to_imgbb(contents)
        return await rpm_from_image_url(image_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rpm-health")
def rpm_health():
    return JSONResponse({
        "ready_player_me_configured": bool(READY_PLAYER_ME_API_URL),
        "imggb_configured": bool(IMGBB_API_KEY),
    })