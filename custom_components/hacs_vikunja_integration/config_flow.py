"""Adds config flow for Vikunja integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    HacsVikunjaIntegrationApiClient,
    HacsVikunjaIntegrationApiClientAuthenticationError,
    HacsVikunjaIntegrationApiClientCommunicationError,
    HacsVikunjaIntegrationApiClientError,
)
from .const import DOMAIN, LOGGER, CONF_API_URL, CONF_API_KEY


class VikunjaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Vikunja."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    api_url=user_input[CONF_API_URL],
                    api_key=user_input[CONF_API_KEY],
                )
            except HacsVikunjaIntegrationApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except HacsVikunjaIntegrationApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except HacsVikunjaIntegrationApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_API_URL],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default=(user_input or {}).get(CONF_API_URL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, api_url: str, api_key: str) -> None:
        """Validate credentials."""
        client = HacsVikunjaIntegrationApiClient(
            api_url=api_url,
            api_key=api_key,
            session=async_create_clientsession(self.hass),
        )
        await client.list_projects()
