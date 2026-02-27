from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


@dataclass
class OpenClawApi:
    base_url: str
    api_token: str
    agent_id: str
    session: aiohttp.ClientSession

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_token}"}

    async def invoke_tool(self, tool: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {
            "tool": tool,
            "args": args or {},
            "sessionKey": "main",
        }
        async with self.session.post(
            self._url("/tools/invoke"),
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def status(self) -> dict[str, Any]:
        # Uses the real Gateway tool-invoke HTTP endpoint.
        return await self.invoke_tool("session_status", {})

    async def chat(self, text: str) -> dict[str, Any]:
        # Requires gateway.http.endpoints.chatCompletions.enabled=true
        payload = {
            "model": "openclaw",
            "messages": [{"role": "user", "content": text}],
            "stream": False,
        }
        headers = {
            **self._auth_headers(),
            "Content-Type": "application/json",
            "x-openclaw-agent-id": self.agent_id,
        }
        async with self.session.post(
            self._url("/v1/chat/completions"),
            headers=headers,
            json=payload,
            timeout=45,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def send_message(self, message: str) -> dict[str, Any]:
        return await self.chat(message)

    async def run_task(self, task: str) -> dict[str, Any]:
        return await self.chat(task)
