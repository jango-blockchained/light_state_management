# Light State Management

## Overview

A Home Assistant custom component that provides advanced light state management capabilities, including state tracking, automated controls, and scene management.

## Features

- Track and manage light states across your Home Assistant instance
- Save and restore custom light scenes
- Automated state management based on conditions
- Transition timing controls
- Group management for multiple lights
- State history logging

## Installation

### Manual Installation

1. Copy the `light_state_management` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add configuration to your `configuration.yaml`

### HACS Installation

1. Add this repository to HACS as a custom repository
2. Install through HACS
3. Restart Home Assistant
4. Add configuration to your `configuration.yaml`

## Configuration

```yaml
light_state_management:
  tracked_lights:
    - light.living_room
    - light.kitchen
    - light.bedroom
  features:
    scene_management: true
    state_restoration: true
    transition_control: true
  default_transition: 2
  history_retention_days: 7
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| tracked_lights | list | required | List of light entities to manage |
| features | map | optional | Enable/disable specific features |
| default_transition | number | 1 | Default transition time in seconds |
| history_retention_days | number | 7 | Days to retain state history |

## Services

### light_state_management.save_scene

Save current light states as a named scene.

```yaml
service: light_state_management.save_scene
data:
  name: "evening_mode"
  lights:
    - light.living_room
    - light.kitchen
```

### light_state_management.restore_scene

Restore a previously saved scene.

```yaml
service: light_state_management.restore_scene
data:
  name: "evening_mode"
```

### light_state_management.clear_history

Clear stored state history.

```yaml
service: light_state_management.clear_history
```

## State Management Rules

You can define rules for automated state management:

```yaml
light_state_management:
  rules:
    - name: "Evening Dimming"
      trigger:
        platform: sun
        event: sunset
      lights:
        - light.living_room
      actions:
        brightness: 50
        transition: 300
```

## Integration with Automations

Example automation using the component:

```yaml
automation:
  - alias: "Evening Scene"
    trigger:
      platform: sun
      event: sunset
    action:
      service: light_state_management.restore_scene
      data:
        name: "evening_mode"
```

## Troubleshooting

- Check Home Assistant logs for component-specific messages
- Ensure all configured lights exist and are accessible
- Verify permissions on storage directory

## Requirements

- Home Assistant 2023.8.0 or newer
- Python 3.9 or newer

## Support

- Report issues on GitHub
- Join our Discord community for support

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.0

- Initial release
- Basic state management features
- Scene support

### v1.1.0

- Added transition controls
- Improved error handling
- Enhanced logging capabilities

```

