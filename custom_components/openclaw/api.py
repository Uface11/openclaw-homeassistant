from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


class OpenClawApiError(Exception):
    """Base OpenClaw API error."""


class OpenClawAuthError(OpenClawApiError):
    """Auth/token related error."""


class OpenClawConnectionError(OpenClawApiError):
    """Connectivity/timeout error."""


class OpenClawHttpError(OpenClawApiError):
    """Generic HTTP error from OpenClaw gateway."""


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

    @staticmethod
    async def _extract_error_body(resp: aiohttp.ClientResponse) -> str:
        try:
            body = await resp.text()
        except Exception:
            body = ""
        return body.strip()

    async def invoke_tool(
        self,
        tool: str,
        args: dict[str, Any] | None = None,
        *,
        session_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tool": tool,
            "args": args or {},
        }
        if session_key:
            payload["sessionKey"] = session_key

        try:
            async with self.session.post(
                self._url("/tools/invoke"),
                headers={**self._auth_headers(), "Content-Type": "application/json", "x-openclaw-agent-id": self.agent_id},
                json=payload,
                timeout=15,
            ) as resp:
                if resp.status in (401, 403):
                    raise OpenClawAuthError("Authentication failed (token invalid or missing permissions)")
                if resp.status >= 400:
                    body = await self._extract_error_body(resp)
                    raise OpenClawHttpError(f"Tool invoke failed ({resp.status}){f': {body}' if body else ''}")
                return await resp.json()
        except aiohttp.ClientConnectorError as err:
            raise OpenClawConnectionError("Cannot connect to OpenClaw Gateway") from err
        except TimeoutError as err:
            raise OpenClawConnectionError("OpenClaw Gateway request timed out") from err

    async def status(self) -> dict[str, Any]:
        return await self.invoke_tool("session_status", {}, session_key="main")

    async def health(self) -> dict[str, Any]:
        return await self.invoke_tool("sessions_list", {"limit": 1, "messageLimit": 0}, session_key="main")

    async def chat(self, text: str, *, session_key: str | None = None) -> dict[str, Any]:
        payload = {
            "model": f"openclaw:{self.agent_id}",
            "messages": [{"role": "user", "content": text}],
            "stream": False,
            "user": "homeassistant",
        }
        headers = {
            **self._auth_headers(),
            "Content-Type": "application/json",
            "x-openclaw-agent-id": self.agent_id,
        }
        if session_key:
            headers["x-openclaw-session-key"] = session_key

        try:
            async with self.session.post(
                self._url("/v1/chat/completions"),
                headers=headers,
                json=payload,
                timeout=45,
            ) as resp:
                if resp.status in (401, 403):
                    raise OpenClawAuthError("Authentication failed (token invalid or missing permissions)")
                if resp.status >= 400:
                    body = await self._extract_error_body(resp)
                    raise OpenClawHttpError(f"Chat completion failed ({resp.status}){f': {body}' if body else ''}")
                return await resp.json()
        except aiohttp.ClientConnectorError as err:
            raise OpenClawConnectionError("Cannot connect to OpenClaw Gateway") from err
        except TimeoutError as err:
            raise OpenClawConnectionError("OpenClaw Gateway request timed out") from err

    async def send_message(self, message: str) -> dict[str, Any]:
        return await self.chat(message)

    async def run_task(self, task: str) -> dict[str, Any]:
        return await self.chat(task)
