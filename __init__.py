"""The Light State Management integration."""
from __future__ import annotations

import logging
import asyncio
import json
from datetime import datetime
from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_HOMEASSISTANT_START,
    EVENT_STATE_CHANGED,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import Event, HomeAssistant, ServiceCall, State, callback
from homeassistant.helpers import entity_registry
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_LIGHTS,
    CONF_MOTION_SENSORS,
    CONF_TRANSITION,
    CONF_SAVE_INTERVAL,
    DEFAULT_TRANSITION,
    DEFAULT_SAVE_INTERVAL,
    SERVICE_SAVE_STATE,
    SERVICE_RESTORE_STATE,
    SERVICE_CLEAR_STATES,
    ATTR_STATES,
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ATTR_XY_COLOR,
    ATTR_EFFECT,
    EVENT_STATE_SAVED,
    EVENT_STATE_RESTORED,
)

_LOGGER = logging.getLogger(__name__)

SAVE_STATE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
})

RESTORE_STATE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
})

CLEAR_STATES_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Light State Management from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    
    manager = LightStateManager(hass, entry)
    domain_data[entry.entry_id] = manager
    
    await manager.async_setup()
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := True:
        manager = hass.data[DOMAIN].pop(entry.entry_id)
        await manager.async_unload()

    return unload_ok

class LightStateManager:
    """Class to manage light states."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the manager."""
        self.hass = hass
        self.entry = entry
        self._states: Dict[str, Dict[str, Any]] = {}
        self._motion_active: Dict[str, bool] = {}
        self._cancel_save_interval = None
        self._setup_complete = False

    async def async_setup(self) -> None:
        """Set up the manager."""
        # Register services
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_SAVE_STATE,
            self._handle_save_state,
            schema=SAVE_STATE_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_RESTORE_STATE,
            self._handle_restore_state,
            schema=RESTORE_STATE_SCHEMA,
        )
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_STATES,
            self._handle_clear_states,
            schema=CLEAR_STATES_SCHEMA,
        )

        # Set up periodic state saving
        save_interval = self.entry.data.get(
            CONF_SAVE_INTERVAL, DEFAULT_SAVE_INTERVAL
        )
        if save_interval > 0:
            self._cancel_save_interval = async_track_time_interval(
                self.hass,
                self._handle_interval_save,
                dt_util.timedelta(seconds=save_interval)
            )

        # Listen for motion sensor state changes
        if motion_sensors := self.entry.data.get(CONF_MOTION_SENSORS):
            @callback
            def handle_motion(event: Event) -> None:
                """Handle motion sensor state changes."""
                entity_id = event.data["entity_id"]
                if entity_id not in motion_sensors:
                    return

                new_state = event.data["new_state"]
                if new_state is None:
                    return

                self._motion_active[entity_id] = new_state.state == STATE_ON
                self._handle_motion_change()

            self.hass.bus.async_listen(EVENT_STATE_CHANGED, handle_motion)

        self._setup_complete = True

    async def async_unload(self) -> None:
        """Unload the manager."""
        if self._cancel_save_interval is not None:
            self._cancel_save_interval()

        self.hass.services.async_remove(DOMAIN, SERVICE_SAVE_STATE)
        self.hass.services.async_remove(DOMAIN, SERVICE_RESTORE_STATE)
        self.hass.services.async_remove(DOMAIN, SERVICE_CLEAR_STATES)

    def _get_light_state(self, state: State) -> dict[str, Any]:
        """Get the relevant state data for a light."""
        attrs = state.attributes
        data = {"state": state.state}

        # Add relevant attributes
        for attr in (
            ATTR_BRIGHTNESS,
            ATTR_COLOR_TEMP,
            ATTR_HS_COLOR,
            ATTR_RGB_COLOR,
            ATTR_XY_COLOR,
            ATTR_EFFECT,
        ):
            if attr in attrs:
                data[attr] = attrs[attr]

        return data

    async def _handle_save_state(self, call: ServiceCall) -> None:
        """Handle the save state service call."""
        entity_ids = call.data[ATTR_ENTITY_ID]
        
        for entity_id in entity_ids:
            if not entity_id.startswith("light."):
                continue

            state = self.hass.states.get(entity_id)
            if state is None:
                continue

            self._states[entity_id] = self._get_light_state(state)
            
            self.hass.bus.fire(
                EVENT_STATE_SAVED,
                {"entity_id": entity_id, "state": self._states[entity_id]}
            )

    async def _handle_restore_state(self, call: ServiceCall) -> None:
        """Handle the restore state service call."""
        entity_ids = call.data[ATTR_ENTITY_ID]
        transition = self.entry.data.get(CONF_TRANSITION, DEFAULT_TRANSITION)

        for entity_id in entity_ids:
            if entity_id not in self._states:
                continue

            state_data = self._states[entity_id]
            if state_data["state"] != STATE_ON:
                continue

            service_data = {"entity_id": entity_id, "transition": transition}
            service_data.update(
                {k: v for k, v in state_data.items() if k != "state"}
            )

            await self.hass.services.async_call(
                "light",
                SERVICE_TURN_ON,
                service_data,
                blocking=True,
            )

            self.hass.bus.fire(
                EVENT_STATE_RESTORED,
                {"entity_id": entity_id, "state": state_data}
            )

    async def _handle_clear_states(self, call: ServiceCall) -> None:
        """Handle the clear states service call."""
        entity_ids = call.data[ATTR_ENTITY_ID]
        
        for entity_id in entity_ids:
            self._states.pop(entity_id, None)

    async def _handle_interval_save(self, now: datetime) -> None:
        """Handle periodic state saving."""
        if not self._setup_complete:
            return

        entity_ids = self.entry.data.get(CONF_LIGHTS, [])
        await self._handle_save_state(
            ServiceCall(DOMAIN, SERVICE_SAVE_STATE, {ATTR_ENTITY_ID: entity_ids})
        )

    def _handle_motion_change(self) -> None:
        """Handle changes in motion sensor states."""
        if not self._setup_complete:
            return

        # If any motion sensor is active, restore states
        if any(self._motion_active.values()):
            entity_ids = self.entry.data.get(CONF_LIGHTS, [])
            self.hass.async_create_task(
                self._handle_restore_state(
                    ServiceCall(
                        DOMAIN,
                        SERVICE_RESTORE_STATE,
                        {ATTR_ENTITY_ID: entity_ids}
                    )
                )
            ) 