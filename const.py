"""Constants for the Light State Management integration."""
from typing import Final

DOMAIN: Final = "light_state_management"

# Configuration
CONF_LIGHTS = "lights"
CONF_MOTION_SENSORS = "motion_sensors"
CONF_TRANSITION = "transition"
CONF_SAVE_INTERVAL = "save_interval"

# Defaults
DEFAULT_TRANSITION = 1.0
DEFAULT_SAVE_INTERVAL = 300  # 5 minutes

# Services
SERVICE_SAVE_STATE = "save_state"
SERVICE_RESTORE_STATE = "restore_state"
SERVICE_CLEAR_STATES = "clear_states"

# Attributes
ATTR_ENTITY_ID = "entity_id"
ATTR_STATES = "states"
ATTR_BRIGHTNESS = "brightness"
ATTR_COLOR_TEMP = "color_temp"
ATTR_HS_COLOR = "hs_color"
ATTR_RGB_COLOR = "rgb_color"
ATTR_XY_COLOR = "xy_color"
ATTR_EFFECT = "effect"

# Events
EVENT_STATE_SAVED = "light_state_saved"
EVENT_STATE_RESTORED = "light_state_restored" 