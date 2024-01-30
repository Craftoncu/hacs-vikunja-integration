"""Define data handling inside home assistant."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    HacsVikunjaIntegrationApiClient,
    HacsVikunjaIntegrationApiClientAuthenticationError,
    HacsVikunjaIntegrationApiClientError,
)
from .const import LOGGER


class VikunjaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Vikunja API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: HacsVikunjaIntegrationApiClient,
        project_id: str
    ) -> None:
        """Initialize."""
        self.client = client
        self._project_id = project_id
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=f"Vikunja Tasks {project_id}",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> list[dict[str, any]]:
        """Update data via Vikunja API."""
        try:
            return await self.client.list_tasks(self._project_id)
        except HacsVikunjaIntegrationApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except HacsVikunjaIntegrationApiClientError as exception:
            raise UpdateFailed(exception) from exception
