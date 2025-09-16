# Fire Control System - AI Assistant Guidelines

## Project Overview

This is a Vietnamese naval fire control system built with PyQt5, featuring real-time CAN bus communication and tactical control interfaces.

## Architecture Overview

### Core Components

- **Main Application** (`main.py`): Entry point with CAN receiver thread
- **Control Panel** (`control_panel/`): Main GUI with tabbed interface
  - `control_panel_main.py`: Main window and tab management
  - `main_tab.py`: Primary control interface with compass, numeric displays
  - `info_tab.py`: Information dashboard with system status cards
  - `log_tab.py`: Event logging interface
  - `setting_tab.py`: Configuration management

### Communication Layer

- **CAN Bus Integration**:
  - `sender.py`: Transmits control commands (18-bit flag system)
  - `receiver.py`: Processes incoming telemetry and targeting data
  - Uses socketcan interface with 500kbps bitrate

### UI Components (`control_panel/components/`)

- **Compass Widgets**: Angular direction displays with animation
- **Numeric Displays**: Real-time data visualization
- **Bullet Widgets**: Trajectory and firing solution displays
- **Custom Message Boxes**: Styled dialog system

## Development Patterns

### Configuration-Driven Design

```python
# Always load config first
with open(resource_path('config.yaml'), 'r') as file:
    self.config = yaml.safe_load(file)

# Use config for widget positioning and styling
widget.setGeometry(
    self.config['Widgets']['CompassLeft']['x'],
    self.config['Widgets']['CompassLeft']['y'],
    self.config['Widgets']['CompassLeft']['width'],
    self.config['Widgets']['CompassLeft']['height']
)
```

### CAN Communication Protocol

```python
# 18-bit flag encoding for control commands
flags = [0]*18
for i in data:
    flags[i-1] = 1
# Pack into 3 bytes and transmit
```

### Animation System

```python
# Use QPropertyAnimation for smooth transitions
self._anim = QPropertyAnimation(self, b"propertyName")
self._anim.setDuration(500)
self._anim.setEasingCurve(QEasingCurve.InOutQuad)
```

## Key Conventions

### Naming Patterns

- Vietnamese UI text: Use full Vietnamese terms (e.g., "Điều khiển", "Thông tin")
- Component classes: PascalCase with descriptive names
- Private methods: `_underscore_prefix`
- Config keys: PascalCase for sections, camelCase for properties

### File Organization

- `control_panel/`: Main application logic
- `control_panel/components/`: Reusable UI widgets
- `assets/`: Icons, images
- Root level: Config files, main entry point

### Error Handling

```python
try:
    # Hardware operations
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
except Exception as e:
    print(f"CAN Error: {e}")
    # Graceful degradation
```

### Threading

```python
# Background CAN receiver
threading.Thread(target=receiver.run, daemon=True).start()
```

## Common Tasks

### Adding New UI Components

1. Create component in `control_panel/components/`
2. Add configuration section in `config.yaml`
3. Import and instantiate in appropriate tab
4. Position using config-driven geometry

### Hardware Integration

1. Define CAN message format in sender/receiver
2. Add data processing logic
3. Update UI components to display new data
4. Test with hardware simulation

## Build & Run Commands

```bash
# Install dependencies
pip install PyQt5 pyyaml python-can scipy numpy pandas

# Run application
python main.py

# CAN interface setup (Linux)
sudo ip link set can0 up type can bitrate 500000
```

## Testing Guidelines

- Test CAN communication with virtual interfaces
- Verify UI responsiveness with animation enabled/disabled
- Validate configuration loading and error handling
