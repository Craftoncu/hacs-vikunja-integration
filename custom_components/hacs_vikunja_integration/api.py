from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout


class HacsVikunjaIntegrationApiClientError(Exception):
    """Exception to indicate a general API error."""


class HacsVikunjaIntegrationApiClientCommunicationError(
    HacsVikunjaIntegrationApiClientError
):
    """Exception to indicate a communication error."""


class HacsVikunjaIntegrationApiClientAuthenticationError(
    HacsVikunjaIntegrationApiClientError
):
    """Exception to indicate an authentication error."""


class HacsVikunjaIntegrationApiClient:
    """Vikunja API Client."""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize Vikunja API Client."""
        self._api_url = api_url.rstrip("/")  # Remove trailing slash if present
        self._api_key = api_key
        self._session = session

    async def list_projects(self) -> list[dict[str, any]]:
        """List all accessable projects"""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-type": "application/json; charset=UTF-8",
        }
        url = f"{self._api_url}/projects"
        return await self._api_wrapper(method="get", url=url, headers=headers)

    async def list_tasks(self, project_id: str) -> list[dict[str, any]]:
        """Get all tasks within projects Vikunja."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-type": "application/json; charset=UTF-8",
        }
        url = f"{self._api_url}/projects/{project_id}/tasks"
        return await self._api_wrapper(method="get", url=url, headers=headers)

    async def update_task(self, task_id: int, done: bool) -> any:
        """Update a task's title in Vikunja."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-type": "application/json; charset=UTF-8",
        }
        data = {"done": done}
        url = f"{self._api_url}/tasks/{task_id}"
        return await self._api_wrapper(method="post", url=url, data=data, headers=headers)

    # async def async_vikunja_delete_task(self, task_id: int) -> any:
    #     """Delete a task in Vikunja."""
    #     headers = {
    #         "Authorization": f"Bearer {self._api_key}",
    #         "Content-type": "application/json; charset=UTF-8",
    #     }
    #     url = f"{self._api_url}/tasks/{task_id}"
    #     return await self._api_wrapper(method="delete", url=url, headers=headers)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise HacsVikunjaIntegrationApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise HacsVikunjaIntegrationApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise HacsVikunjaIntegrationApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise HacsVikunjaIntegrationApiClientError(
                "Something really wrong happened!"
            ) from exception