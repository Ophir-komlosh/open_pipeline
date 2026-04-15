from consts import *
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import uuid

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(FULL_PATH)
async def chat_completions(request: Request):
    body = await request.json()
    request_id = str(uuid.uuid4())

    headers = {
        AUTH_HEADER: AUTH_PROMPT,
        CONTENT_TYPE_HEADER: CONTENT_TYPE_PROMPT,
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}{COMPLETIONS_PATH}",
                json=body,
                headers=headers,
            )

        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "error": "upstream_error",
                    "details": response.text,
                    "request_id": request_id
                },
            )

        return response.json()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "details": str(e),
                "request_id": request_id
            },
        )