# Open Pipeline

## Overview

This project implements a **FastAPI middleware proxy service** that sits between a WebUI client and the OpenAI API.

```
User → Open WebUI → Middleware → OpenAI API
```

The middleware intercepts requests, prepends a system prompt, and forwards them to OpenAI while maintaining full API compatibility.

---

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint  
- `/v1/models` endpoint for WebUI integration  
- System prompt injection into all requests  
- Streaming support (Server-Sent Events)  
- Structured error handling with request tracing  
- Health and readiness endpoints  
- Unit tests covering core logic  

---

## How to Run

### 1. Set environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

### 2. Run the system

```bash
docker-compose up --build
```

### 3. Open WebUI

Access the WebUI in your browser:
http://localhost:3000
and select the available model.

---

## Configuration

The WebUI is configured to use the middleware:

```yaml
OPENAI_API_BASE_URL=http://middleware:8000/v1
```

---

## API Endpoints

### Chat Completions

```
POST /v1/chat/completions
```

- Fully compatible with OpenAI API  
- Supports both streaming and non-streaming responses  

---

### Models

```
GET /v1/models
```

Returns available models in OpenAI-compatible format.

---

### Health Check

```
GET /health
```

Returns basic service status.

---

### Readiness Check

```
GET /ready
```

Indicates whether the service is ready and properly configured.

---

## Design Decisions

### Middleware as OpenAI-compatible proxy

The middleware preserves OpenAI API structure so existing clients (like WebUI) can work without modification.

---

### System Prompt Injection

The middleware injects a system prompt into every request:

- If no system message exists → it is prepended  
- If a system message exists → it is merged  

This ensures consistent behavior without breaking user intent.

---

### Streaming Implementation

Streaming responses are handled using FastAPI’s `StreamingResponse`.

The middleware:

- opens a streaming connection to OpenAI  
- forwards chunks transparently 
- preserves SSE format  

This avoids reprocessing and minimizes latency.

---

### Error Handling

Errors from OpenAI are:

- captured and normalized  
- returned with a consistent structure  
- tagged with a `request_id` for traceability  

Streaming errors are wrapped in SSE format to maintain protocol consistency.

---

### Why support both stream and non-stream

Although WebUI defaults to streaming, the middleware supports both modes to remain fully compatible with the OpenAI API contract.

---



### Static vs dynamic model listing

I considered two approaches for the `/v1/models` endpoint:

- **Static model list**: return a small fixed set of supported models. I chose `gpt-4o-mini` due to its low quickness, efficiency, and reliability.
- **Dynamic upstream proxy**: fetch the available models from OpenAI and return them directly.

I chose the **static model list** approach for this assignment.

#### Why this decision

A static model list provides a more predictable and controlled environment for a take-home assignment. It reduces external dependencies and ensures that the model exposed in the UI is guaranteed to be one the middleware can successfully forward and support end-to-end.

It also allows explicit control over which models are exposed, avoiding accidental usage of unsupported or higher-cost models.

A dynamic `/v1/models` proxy is more flexible and closer to a transparent proxy, but it introduces additional failure modes such as upstream availability issues, authentication dependencies, and the need for filtering and policy decisions around which models should be exposed.

#### Tradeoff

From my perspective, a **dynamic model proxy** is the more extensible design because it preserves upstream behavior and reduces manual dependecy.

However, for this assignment I prioritized **a stable end-to-end demo** over additional extensibility.

If this service was to be extended, I would have made `/v1/models` a dynamic upstream-backed implementation.


## Testing

Unit tests cover:

- prompt injection logic  
- request validation  
- endpoint responses  
- error handling  
- readiness and health checks  

Run tests with:

```bash
pytest -v
```

---

## Prompt Design Notes

I designed this prompt to make the middleware enforce a deterministic extraction contract across many document types.

### Why this structure

I used a fixed schema so the output is predictable and easy to consume. The schema separates:

- document classification  
- concise summarization  
- extracted fields  
- uncertainty handling  

This makes the output useful both for humans and downstream systems.

---

### Why confidence is attached per field

Confidence is attached to each extracted field because uncertainty is usually local, not global.

---

### Why `uncertain_fields` exists separately

A separate uncertainty section makes ambiguity explicit and auditable. This helps avoid silent hallucination and preserves transparency when the input is noisy, incomplete, or contradictory.

---

### Why follow-up behavior is separated

The assignment requires normal responses for follow-up questions. I explicitly separated extraction mode from follow-up mode so the model does not keep forcing JSON when the user is asking a natural question about already extracted information.

---

### Edge cases considered

The prompt handles:

- noisy OCR-like input  
- partially missing fields  
- contradictory values  
- multiple entities in one text  
- mixed document types  
- empty input  

---

### Iteration goals

The prompt was structured to prioritize:

1. strict schema compliance  
2. minimal hallucination  
3. robustness to messy input  
4. compatibility with conversational follow-up  
