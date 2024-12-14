"""Config flow for Light State Management integration."""
from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.entity_registry import async_get

from .const import (
    DOMAIN,
    CONF_LIGHTS,
    CONF_MOTION_SENSORS,
    CONF_TRANSITION,
    CONF_SAVE_INTERVAL,
    DEFAULT_TRANSITION,
    DEFAULT_SAVE_INTERVAL,
)

class LightStateManagementConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Light State Management."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Light State Management",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LIGHTS): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
                vol.Optional(CONF_MOTION_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class="motion",
                        multiple=True
                    )
                ),
                vol.Optional(
                    CONF_TRANSITION,
                    default=DEFAULT_TRANSITION
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=10,
                        step=0.1,
                        unit_of_measurement="seconds"
                    )
                ),
                vol.Optional(
                    CONF_SAVE_INTERVAL,
                    default=DEFAULT_SAVE_INTERVAL
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=60,
                        max=3600,
                        step=60,
                        unit_of_measurement="seconds"
                    )
                ),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow changes."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_LIGHTS,
                    default=self.config_entry.options.get(
                        CONF_LIGHTS,
                        self.config_entry.data.get(CONF_LIGHTS, [])
                    )
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
                vol.Optional(
                    CONF_MOTION_SENSORS,
                    default=self.config_entry.options.get(
                        CONF_MOTION_SENSORS,
                        self.config_entry.data.get(CONF_MOTION_SENSORS, [])
                    )
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class="motion",
                        multiple=True
                    )
                ),
                vol.Optional(
                    CONF_TRANSITION,
                    default=self.config_entry.options.get(
                        CONF_TRANSITION,
                        self.config_entry.data.get(
                            CONF_TRANSITION,
                            DEFAULT_TRANSITION
                        )
                    )
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=10,
                        step=0.1,
                        unit_of_measurement="seconds"
                    )
                ),
                vol.Optional(
                    CONF_SAVE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SAVE_INTERVAL,
                        self.config_entry.data.get(
                            CONF_SAVE_INTERVAL,
                            DEFAULT_SAVE_INTERVAL
                        )
                    )
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=60,
                        max=3600,
                        step=60,
                        unit_of_measurement="seconds"
                    )
                ),
            })
        ) 