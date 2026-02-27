from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


@dataclass
class OpenClawApi:
    base_url: str
    api_token: str
    session: aiohttp.ClientSession

    async def status(self) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/status"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        async with self.session.get(url, headers=headers, timeout=10) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def send_message(self, message: str) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/message"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"message": message}
        async with self.session.post(url, headers=headers, json=payload, timeout=20) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def run_task(self, task: str) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/task"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"task": task}
        async with self.session.post(url, headers=headers, json=payload, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.json()
