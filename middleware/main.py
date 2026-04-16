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
async def chat_completions(request: Request) -> JSONResponse:
    body = await request.json()
    request_id = str(uuid.uuid4())

    if not OPENAI_API_KEY:
        return send_error_response(INTERNAL_SERVER_ERROR_CODE, CONFIGURATION_ERROR, "OPENAI_API_KEY is not set", request_id) 

    messages = body.get("messages")

    if not isinstance(messages, list) or len(messages) == EMPTY_MESSAGE_LENGTH:
        return send_error_response(BAD_REQUEST_CODE, INVALID_REQUEST, "'messages' must be a non-empty list", request_id) 

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

        if response.status_code != OK_STATUS_CODE:
            return send_error_response(response.status_code, "upstream_error", "response.text", request_id) 
        
        return response.json()

    except Exception as e:
        return send_error_response(INTERNAL_SERVER_ERROR_CODE, "internal_error", str(e), request_id)


def send_error_response(status_code: int, error_type: str, details: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "details": details,
            "request_id": request_id
        },
    )