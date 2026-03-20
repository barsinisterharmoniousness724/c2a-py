from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import Settings, get_settings
from constants import CLAUDE_IDENTITY_RESPONSE, is_identity_probe, is_refusal, sanitize_response
from converter import (
    convert_to_cursor_request,
    estimate_input_tokens,
    last_user_text,
    parse_tool_calls,
    short_id,
)
from cursor_client import send_cursor_request
from schemas import AnthropicRequest, CountTokensResponse

app = FastAPI(title="cursor2api-py", version="0.1.0")
bearer = HTTPBearer(auto_error=False)


def get_settings_dep() -> Settings:
    return get_settings()


async def require_api_token(
    settings: Settings = Depends(get_settings_dep),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_api_key: str | None = Header(default=None),
) -> None:
    if not settings.auth_tokens:
        return
    token = x_api_key or (credentials.credentials if credentials else None)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token. Use Authorization: Bearer <token>.",
        )
    if token not in settings.auth_tokens:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token.",
        )


def build_message_response(body: AnthropicRequest, text: str, settings: Settings) -> dict[str, Any]:
    response_text = sanitize_response(text) if settings.sanitize_response else text
    tool_calls, clean_text = parse_tool_calls(response_text)

    if is_refusal(clean_text) and not tool_calls:
        clean_text = CLAUDE_IDENTITY_RESPONSE

    content: list[dict[str, Any]] = []
    if clean_text:
        content.append({"type": "text", "text": clean_text})
    for tool_call in tool_calls:
        content.append(
            {
                "type": "tool_use",
                "id": short_id("toolu_"),
                "name": tool_call["name"],
                "input": tool_call["arguments"],
            }
        )

    return {
        "id": short_id("msg_"),
        "type": "message",
        "role": "assistant",
        "content": content or [{"type": "text", "text": ""}],
        "model": body.model,
        "stop_reason": "tool_use" if tool_calls else "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": estimate_input_tokens(body),
            "output_tokens": max(1, len(response_text) // 4),
        },
    }


def encode_sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def anthropic_stream(payload: dict[str, Any]):
    yield encode_sse(
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": payload["id"],
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": payload["model"],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {
                    "input_tokens": payload["usage"]["input_tokens"],
                    "output_tokens": 0,
                },
            },
        },
    )

    for index, block in enumerate(payload["content"]):
        if block["type"] == "text":
            yield encode_sse(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": index,
                    "content_block": {"type": "text", "text": ""},
                },
            )
            if block.get("text"):
                yield encode_sse(
                    "content_block_delta",
                    {
                        "type": "content_block_delta",
                        "index": index,
                        "delta": {"type": "text_delta", "text": block["text"]},
                    },
                )
            yield encode_sse(
                "content_block_stop",
                {"type": "content_block_stop", "index": index},
            )
            continue

        if block["type"] == "tool_use":
            yield encode_sse(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": index,
                    "content_block": block,
                },
            )
            yield encode_sse(
                "content_block_stop",
                {"type": "content_block_stop", "index": index},
            )

    yield encode_sse(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {
                "stop_reason": payload["stop_reason"],
                "stop_sequence": None,
            },
            "usage": {"output_tokens": payload["usage"]["output_tokens"]},
        },
    )
    yield encode_sse("message_stop", {"type": "message_stop"})


async def handle_messages(body: AnthropicRequest, settings: Settings) -> JSONResponse | StreamingResponse:
    prompt = last_user_text(body)
    if not body.tools and is_identity_probe(prompt):
        mock = build_message_response(body, CLAUDE_IDENTITY_RESPONSE, settings)
        if body.stream:
            return StreamingResponse(anthropic_stream(mock), media_type="text/event-stream")
        return JSONResponse(mock)

    cursor_payload = convert_to_cursor_request(body, settings)
    try:
        cursor_text = await send_cursor_request(cursor_payload, settings)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    response_payload = build_message_response(body, cursor_text, settings)
    if body.stream:
        return StreamingResponse(anthropic_stream(response_payload), media_type="text/event-stream")
    return JSONResponse(response_payload)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.detail, "type": "api_error"}},
    )


@app.get("/")
async def root(settings: Settings = Depends(get_settings_dep)):
    return {
        "name": "cursor2api-py",
        "version": app.version,
        "description": "Minimal FastAPI proxy for Claude Code-compatible Anthropic Messages requests.",
        "endpoints": {
            "anthropic_messages": "POST /v1/messages",
            "count_tokens": "POST /v1/messages/count_tokens",
            "models": "GET /v1/models",
            "health": "GET /health",
        },
        "cursor_target": settings.cursor_chat_api,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}


@app.get("/v1/models")
async def list_models(settings: Settings = Depends(get_settings_dep)):
    return {
        "object": "list",
        "data": [
            {"id": settings.cursor_model, "object": "model", "owned_by": "anthropic"},
            {"id": "claude-sonnet-4-20250514", "object": "model", "owned_by": "anthropic"},
            {"id": "claude-3-5-sonnet-20241022", "object": "model", "owned_by": "anthropic"},
        ],
    }


@app.post("/v1/messages/count_tokens", dependencies=[Depends(require_api_token)], response_model=CountTokensResponse)
@app.post("/messages/count_tokens", dependencies=[Depends(require_api_token)], response_model=CountTokensResponse)
async def count_tokens(body: AnthropicRequest):
    return CountTokensResponse(input_tokens=estimate_input_tokens(body))


@app.post("/v1/messages", dependencies=[Depends(require_api_token)])
@app.post("/messages", dependencies=[Depends(require_api_token)])
async def messages(body: AnthropicRequest, settings: Settings = Depends(get_settings_dep)):
    return await handle_messages(body, settings)
