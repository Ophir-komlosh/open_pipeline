import json

from consts import *
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from prompt_injector import inject_system_prompt
import httpx
import uuid

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get(FULL_MODELS_PATH)
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "owned_by": "middleware"
            }
        ]
    }


async def post_openai_response(body: dict, headers: dict, request_id: str) -> JSONResponse:
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"{OPENAI_BASE_URL}{COMPLETIONS_PATH}",
            json=body,
            headers=headers,
        )

        if response.status_code != OK_STATUS_CODE:
            return create_error_response(response.status_code, UPSTREAM_ERROR, response.text, request_id) 
        
        return response.json()


async def stream_openai_response(body: dict, headers: dict, request_id: str):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(HTTP_POST,
            f"{OPENAI_BASE_URL}{COMPLETIONS_PATH}",
            json=body,
            headers=headers,
        ) as response:

            if response.status_code != OK_STATUS_CODE:
                error_text = await response.aread()

                try:
                    error_details = json.loads(error_text.decode())
                except Exception:
                    error_details = {"raw_error": error_text.decode()}

                payload = {
                    "error": UPSTREAM_ERROR,
                    "details": error_details,
                    "request_id": request_id,
                }

                yield f"data: {json.dumps(payload)}\n\n".encode()
                return

            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk


@app.post(FULL_COMPLETIONS_PATH)
async def chat_completions(request: Request) -> JSONResponse:
    body = await request.json()
    request_id = str(uuid.uuid4())

    if not OPENAI_API_KEY:
        return create_error_response(INTERNAL_SERVER_ERROR_CODE, CONFIGURATION_ERROR, "OPENAI_API_KEY is not set", request_id) 

    messages = body.get("messages")

    if not isinstance(messages, list) or len(messages) == EMPTY_MESSAGE_LENGTH:
        return create_error_response(BAD_REQUEST_CODE, INVALID_REQUEST, "'messages' must be a non-empty list", request_id) 
    
    body["messages"] = inject_system_prompt(messages, SYSTEM_PROMPT)
    stream = body.get("stream", False)

    headers = {
        AUTH_HEADER: AUTH_PROMPT,
        CONTENT_TYPE_HEADER: CONTENT_TYPE_PROMPT,
    }
    
    try:
        if stream:
            return StreamingResponse(
                stream_openai_response(body, headers, request_id),
                media_type=STREAM_MEDIA_TYPE,
            )

        return await post_openai_response(body, headers, request_id)

    except Exception as e:
        return create_error_response(INTERNAL_SERVER_ERROR_CODE, INTERNAL_ERROR, str(e), request_id)


def create_error_response(status_code: int, error_type: str, details: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "details": details,
            "request_id": request_id
        },
    )