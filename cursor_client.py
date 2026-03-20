from __future__ import annotations

import json
from typing import Any

import httpx

from config import Settings


def build_cursor_headers(settings: Settings) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "sec-ch-ua-platform": '"Windows"',
        "x-path": "/api/chat",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "x-method": "POST",
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-platform-version": '"19.0.0"',
        "origin": "https://cursor.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://cursor.com/",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "priority": "u=1, i",
        "user-agent": settings.user_agent,
        "x-is-human": "",
    }


async def send_cursor_request(payload: dict[str, Any], settings: Settings) -> str:
    headers = build_cursor_headers(settings)
    chunks: list[str] = []

    async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
        async with client.stream(
            "POST",
            settings.cursor_chat_api,
            headers=headers,
            json=payload,
        ) as response:
            if response.status_code >= 400:
                body = await response.aread()
                raise httpx.HTTPStatusError(
                    f"Cursor API error: HTTP {response.status_code} - {body.decode('utf-8', errors='replace')}",
                    request=response.request,
                    response=response,
                )

            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                raw = line[6:].strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "text-delta" and event.get("delta"):
                    chunks.append(str(event["delta"]))

    return "".join(chunks)
