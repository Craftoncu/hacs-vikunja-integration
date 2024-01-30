from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HacsVikunjaIntegrationApiClient
from .const import DOMAIN, CONF_API_URL, CONF_API_KEY
from .coordinator import VikunjaDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.TODO]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    client = HacsVikunjaIntegrationApiClient(
        api_url=entry.data[CONF_API_URL],
        api_key=entry.data[CONF_API_KEY],
        session=async_get_clientsession(hass),
    )

    # Fetch all projects from Vikunja
    projects = await client.list_projects()

    # Create a coordinator for each project
    for project in projects:
        coordinator = VikunjaDataUpdateCoordinator(
            hass=hass,
            client=client,
            project_id=project['id'],
        )
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][f"project_{project['id']}"] = coordinator


    hass.data[DOMAIN][entry.entry_id] = client


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
