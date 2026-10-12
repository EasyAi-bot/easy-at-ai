from __future__ import annotations
import io, os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
app = FastAPI(title='easy@Ai Cloud AI Bridge', version='1.0.0', docs_url=None, redoc_url=None, openapi_url=None)

class ImageRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=12000)
    model: str = 'black-forest-labs/FLUX.1-schnell'




def get_token(authorization: Optional[str]) -> str:
    # Use the private token saved in Render first.
    token = os.environ.get("HF_TOKEN", "").strip()

    # If no Render token exists, allow a token supplied by the website.
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No Hugging Face token is configured. Add HF_TOKEN in Render Environment Variables."
        )

    if not token.startswith("hf_"):
        raise HTTPException(
            status_code=401,
            detail="The Hugging Face token format is invalid. Check the token configured in Render."
        )

    return token



def provider_error(exc: Exception) -> HTTPException:
    message = str(exc)
    low = message.lower()
    if any(x in low for x in ('401', 'unauthorized', 'invalid token', 'authentication')):
        detail = 'Hugging Face rejected the token. Check that it is valid and has “Make calls to Inference Providers” permission.'
    elif any(x in low for x in ('402', 'payment', 'billing', 'credit', 'quota')):
        detail = 'The provider reports that free credits or quota are unavailable for this request. No paid fallback is configured. Check your Hugging Face Inference Providers billing page before retrying.'
    elif any(x in low for x in ('503', 'loading', 'not available', 'no provider', 'not supported')):
        detail = 'This model/provider may be unavailable or not supported for this task right now. Try again later or select a supported model.'
    elif any(x in low for x in ('timeout', 'timed out')):
        detail = 'The generation timed out. The model may be busy; wait a moment and retry.'
    else:
        detail = 'Generation failed. Provider details: ' + message[:700]
    return HTTPException(status_code=502, detail=detail)

@app.get('/')
def index():
    return FileResponse(BASE / 'index.html')

@app.get('/api/health')
def health():
    return {'ok': True, 'service': 'easy@Ai cloud bridge', 'image_generation': 'Hugging Face Inference Providers', 'video_generation': 'Hugging Face Inference Providers','token_storage': 'Render environment variable'}

@app.post('/api/image')
def generate_image(req: ImageRequest, authorization: Optional[str] = Header(default=None)):
    token = get_token(authorization)
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token, provider='auto', timeout=180)
        image = client.text_to_image(req.prompt, model=req.model)
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        return Response(content=buf.getvalue(), media_type='image/png', headers={'Cache-Control': 'no-store'})
    except HTTPException:
        raise
    except Exception as exc:
        raise provider_error(exc)


@app.post('/api/check-token')
def check_token(authorization: Optional[str] = Header(default=None)):
    token = get_token(authorization)
    try:
        from huggingface_hub import HfApi
        user = HfApi(token=token).whoami()
        return {'ok': True, 'username': user.get('name', 'Hugging Face user'), 'note': 'Token is valid. Inference permission and provider quota are confirmed only when a generation request succeeds.'}
    except Exception as exc:
        raise provider_error(exc)

@app.post('/api/image-edit')
async def generate_reference_image(
    prompt: str = Form(...),
    model: str = Form('Qwen/Qwen-Image-Edit'),
    image: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
):
    token = get_token(authorization)
    if len(prompt) > 12000:
        raise HTTPException(status_code=413, detail='Prompt is too long. Keep it under 12,000 characters.')
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail='Upload a reference image first.')
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='Please use a reference image smaller than 12 MB.')
    if not (image.content_type or '').startswith('image/'):
        raise HTTPException(status_code=415, detail='The reference file must be an image.')
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token, provider='auto', timeout=240)
        edited = client.image_to_image(image=content, prompt=prompt, model=model)
        buf = io.BytesIO()
        edited.save(buf, format='PNG')
        return Response(content=buf.getvalue(), media_type='image/png', headers={'Cache-Control': 'no-store'})
    except HTTPException:
        raise
    except Exception as exc:
        raise provider_error(exc)

@app.post('/api/video')
async def generate_video(
    prompt: str = Form(...),
    model: str = Form('Wan-AI/Wan2.2-I2V-A14B'),
    image: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
):
    token = get_token(authorization)
    if len(prompt) > 6000:
        raise HTTPException(status_code=413, detail='Prompt is too long. Keep it under 6,000 characters.')
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail='Upload a starting image first.')
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='Please use an image smaller than 12 MB.')
    if not (image.content_type or '').startswith('image/'):
        raise HTTPException(status_code=415, detail='The starting file must be an image.')
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token, provider='auto', timeout=600)
        video = client.image_to_video(image=content, prompt=prompt, model=model)
        if hasattr(video, 'read'):
            video = video.read()
        return Response(content=bytes(video), media_type='video/mp4', headers={'Cache-Control': 'no-store'})
    except HTTPException:
        raise
    except Exception as exc:
        raise provider_error(exc)

if __name__ == '__main__':
    import uvicorn
    # Local-only by default: avoids exposing the token bridge to other devices on the network.
    uvicorn.run(app, host=os.environ.get('EASYAI_HOST', '127.0.0.1'), port=int(os.environ.get('EASYAI_PORT', '8765')))
