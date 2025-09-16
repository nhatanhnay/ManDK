# -*- coding: utf-8 -*-
"""
Application constants - Centralized constants to eliminate magic numbers.
All hardcoded values should be defined here for consistency and maintainability.
"""

# UI Constants
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
TAB_HEIGHT = 34
TAB_WIDTH = 220
TAB_GAP = 8
TAB_VERTICAL_OFFSET = 6
TAB_BORDER_RADIUS = 8

# Timer Intervals (milliseconds)
DATA_UPDATE_INTERVAL = 1000
ANIMATION_TIMER_INTERVAL = 1000
SIMULATION_UPDATE_INTERVAL = 1000

# Grid and Layout Constants
GRID_SPACING = 50
ISOMETRIC_OFFSET_X = 3
ISOMETRIC_OFFSET_Y = 6
ISOMETRIC_BUTTON_HEIGHT = 80
BUTTON_BORDER_RADIUS = 8

# Data Management Constants
MAX_HISTORY_RECORDS = 1000
MAX_PARAMETER_HISTORY = 100
BACKUP_RETENTION_LIMIT = 50

# Network Constants
CAN_BITRATE = 500000
CAN_CHANNEL = 'can0'

# Color Constants
class Colors:
    """Common color values used throughout the application."""

    # Background Colors
    MAIN_BACKGROUND = "#121212"
    TAB_BACKGROUND = "#1e5c6b"
    TRANSPARENT = "transparent"

    # Text Colors
    PRIMARY_TEXT = "#E6EEF3"
    SECONDARY_TEXT = "rgba(230,238,243,0.7)"

    # Border Colors
    WHITE_BORDER = "#FFFFFF"
    BLACK_BORDER = "#000000"
    TRANSPARENT_WHITE_BORDER = "#30ffffff"

    # Status Colors
    STATUS_NORMAL = "#00ff00"
    STATUS_WARNING = "#ffff00"
    STATUS_ERROR = "#ff0000"

    # Button States
    BUTTON_HOVER = "#444444"
    BUTTON_PRESSED = "#333333"

# File and Path Constants
class Paths:
    """File path constants."""

    CONFIG_FILE = 'config.yaml'
    CUSTOM_CONFIG_DIR = 'data'
    CUSTOM_CONFIG_FILE = 'system_config_custom.json'
    ASSETS_DIR = 'assets'
    ICONS_DIR = 'assets/Icons'
    VIETNAM_FLAG_ICON = 'assets/Icons/Vietnam.png'

# System Configuration Constants
class SystemLimits:
    """System limits and thresholds."""

    # Electrical Limits
    DEFAULT_MIN_VOLTAGE = 8.0
    DEFAULT_MAX_VOLTAGE = 15.0
    DEFAULT_MAX_CURRENT = 8.0
    DEFAULT_MAX_TEMPERATURE = 70.0

    # Power Thresholds
    HIGH_POWER_THRESHOLD = 100.0
    CRITICAL_POWER_THRESHOLD = 1000.0

    # Validation Tolerances
    POWER_CALCULATION_TOLERANCE = 10.0  # Percentage
    CURRENT_WARNING_THRESHOLD = 1.2     # 20% over limit
    TEMPERATURE_WARNING_THRESHOLD = 1.1  # 10% over limit

    # Animation and UI
    ALPHA_OPAQUE = 255
    ALPHA_SEMI_TRANSPARENT = 128
    ALPHA_QUARTER = 64

# Weapon System Constants
class WeaponSystem:
    """Constants related to weapon systems."""

    AMMO_SLOTS_PER_SIDE = 18
    BULLET_GRID_ROWS = 3
    BULLET_GRID_COLS = 6

    # Default directions and angles
    DEFAULT_DIRECTION = 0
    DEFAULT_ANGLE = 0
    DEFAULT_DISTANCE = 0
    DEFAULT_SHIP_DIRECTION = 30  # degrees from North

# Font Constants
class Fonts:
    """Font specifications."""

    DEFAULT_FAMILY = "Tahoma"
    DEFAULT_SIZE = 18
    BUTTON_FONT_WEIGHT = "Bold"

# Animation Constants
class Animation:
    """Animation-related constants."""

    DEPTH_READY = 5.0
    DEPTH_SELECTED = 2.5
    DEPTH_DISABLED = 2.5
    ISOMETRIC_FACTOR = 0.7

    # Shadow parameters
    SHADOW_OFFSET_PRESSED = 2
    SHADOW_OFFSET_NORMAL = 4
    SHADOW_OPACITY_PRESSED = 30
    SHADOW_OPACITY_NORMAL = 60