"""
Configuration Module - Centralized constants και settings
"""

from dataclasses import dataclass


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AppConfig:
    """Γενικές ρυθμίσεις εφαρμογής"""
    APP_NAME: str = "HVACR Maintenance System"
    APP_VERSION: str = "2.0"
    DATABASE_NAME: str = "hvacr_maintenance.db"
    SETTINGS_FILE: str = "settings.json"


# ═══════════════════════════════════════════════════════════════════════════
# UI CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UIConfig:
    """UI layout και dimensions"""
    
    # Window dimensions
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 800
    WINDOW_MIN_WIDTH: int = 1200
    WINDOW_MIN_HEIGHT: int = 700
    
    # Sidebar
    SIDEBAR_WIDTH: int = 220
    SIDEBAR_BUTTON_WIDTH: int = 200
    SIDEBAR_BUTTON_HEIGHT: int = 45
    
    # Card dimensions
    TASK_CARD_HEIGHT: int = 65
    TASK_CARD_COMPACT_HEIGHT: int = 45
    STAT_CARD_MIN_WIDTH: int = 200
    
    # Form elements
    FORM_INPUT_WIDTH: int = 300
    FORM_INPUT_HEIGHT: int = 32
    FORM_BUTTON_WIDTH: int = 150
    FORM_BUTTON_HEIGHT: int = 40
    FORM_TEXTBOX_HEIGHT: int = 80
    FORM_NOTES_HEIGHT: int = 60
    
    # Calendar
    CALENDAR_WIDTH: int = 400
    CALENDAR_HEIGHT: int = 450
    
    # Chain preview
    CHAIN_PREVIEW_HEIGHT: int = 300
    
    # Padding values
    PADDING_TINY: int = 3
    PADDING_SMALL: int = 5
    PADDING_MEDIUM: int = 10
    PADDING_LARGE: int = 20
    PADDING_XLARGE: int = 40
    
    # Corner radius
    CORNER_RADIUS_SMALL: int = 6
    CORNER_RADIUS_MEDIUM: int = 10
    CORNER_RADIUS_LARGE: int = 15
    
    # Border width
    BORDER_WIDTH_THIN: int = 1
    BORDER_WIDTH_MEDIUM: int = 2
    BORDER_WIDTH_THICK: int = 3


# ═══════════════════════════════════════════════════════════════════════════
# FONT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FontConfig:
    """Font settings"""
    
    # Font family
    FONT_FAMILY: str = "Segoe UI"
    
    # Base font sizes (before scaling)
    FONT_SIZE_TITLE_LARGE: int = 32
    FONT_SIZE_TITLE: int = 24
    FONT_SIZE_SUBTITLE: int = 20
    FONT_SIZE_HEADING: int = 18
    FONT_SIZE_BODY: int = 13
    FONT_SIZE_INPUT: int = 15
    FONT_SIZE_SMALL: int = 11
    FONT_SIZE_TINY: int = 9
    FONT_SIZE_STAT_VALUE: int = 36
    
    # Font scale limits
    FONT_SCALE_MIN: float = 0.8
    FONT_SCALE_MAX: float = 1.5
    FONT_SCALE_DEFAULT: float = 1.0
    FONT_SCALE_STEPS: int = 14


# ═══════════════════════════════════════════════════════════════════════════
# COLOR THEMES
# ═══════════════════════════════════════════════════════════════════════════

class ColorThemes:
    """Color themes για dark και light mode"""
    
    DARK = {
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2b2b2b",
        "bg_tertiary": "#3a3a3a",
        "card_bg": "#2b2b2b",
        "card_border": "#404040",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "text_disabled": "#666666",
        "accent_blue": "#3B8ED0",
        "accent_green": "#28a745",
        "accent_orange": "#ffa500",
        "accent_red": "#dc3545",
        "sidebar_bg": "#1e1e1e",
        "sidebar_hover": "#2d2d2d",
    }
    
    LIGHT = {
        "bg_primary": "#f0f0f0",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e8e8e8",
        "card_bg": "#ffffff",
        "card_border": "#d0d0d0",
        "text_primary": "#000000",
        "text_secondary": "#555555",
        "text_disabled": "#999999",
        "accent_blue": "#1E5A8E",
        "accent_green": "#1e7e34",
        "accent_orange": "#e67e00",
        "accent_red": "#c82333",
        "sidebar_bg": "#e0e0e0",
        "sidebar_hover": "#d0d0d0",
    }


# ═══════════════════════════════════════════════════════════════════════════
# BUTTON STYLES
# ═══════════════════════════════════════════════════════════════════════════

class ButtonStyles:
    """Button style configurations"""
    
    @staticmethod
    def get_style(button_type: str, theme: dict) -> dict:
        """
        Επιστρέφει button styling με 3D effect.
        
        Args:
            button_type: "primary", "success", "danger", "secondary", "special"
            theme: Current theme dictionary
        
        Returns:
            Dict με button style properties
        """
        styles = {
            "primary": {
                "fg_color": theme["accent_blue"],
                "hover_color": "#2d6ca3",
                "text_color": "white",
                "corner_radius": UIConfig.CORNER_RADIUS_MEDIUM,
                "border_width": UIConfig.BORDER_WIDTH_MEDIUM,
                "border_color": "#5AA3D9"
            },
            "success": {
                "fg_color": theme["accent_green"],
                "hover_color": "#218838",
                "text_color": "white",
                "corner_radius": UIConfig.CORNER_RADIUS_MEDIUM,
                "border_width": UIConfig.BORDER_WIDTH_MEDIUM,
                "border_color": "#4FD664"
            },
            "danger": {
                "fg_color": theme["accent_red"],
                "hover_color": "#bd2130",
                "text_color": "white",
                "corner_radius": UIConfig.CORNER_RADIUS_MEDIUM,
                "border_width": UIConfig.BORDER_WIDTH_MEDIUM,
                "border_color": "#FF5A6E"
            },
            "secondary": {
                "fg_color": theme["bg_tertiary"],
                "hover_color": theme["card_border"],
                "text_color": theme["text_primary"],
                "corner_radius": UIConfig.CORNER_RADIUS_MEDIUM,
                "border_width": UIConfig.BORDER_WIDTH_MEDIUM,
                "border_color": theme["card_border"]
            },
            "special": {
                "fg_color": "#6C63FF",
                "hover_color": "#5549CC",
                "text_color": "white",
                "corner_radius": UIConfig.CORNER_RADIUS_MEDIUM,
                "border_width": UIConfig.BORDER_WIDTH_MEDIUM,
                "border_color": "#9B93FF"
            }
        }
        
        return styles.get(button_type, styles["primary"])


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DatabaseConfig:
    """Database settings"""
    
    # Connection pool settings (για μελλοντική χρήση)
    MAX_CONNECTIONS: int = 10
    CONNECTION_TIMEOUT: int = 30  # seconds
    
    # Query limits
    MAX_RECENT_TASKS: int = 10
    MAX_SEARCH_RESULTS: int = 100
    
    # Soft delete flag values
    ACTIVE: int = 0
    DELETED: int = 1
    PERMANENTLY_DELETED: int = 2


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION RULES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationRules:
    """Validation rules για input fields"""
    
    # Group validation
    GROUP_NAME_MIN_LENGTH: int = 2
    GROUP_NAME_MAX_LENGTH: int = 100
    
    # Unit validation
    UNIT_NAME_MIN_LENGTH: int = 2
    UNIT_NAME_MAX_LENGTH: int = 100
    SERIAL_NUMBER_MAX_LENGTH: int = 50
    
    # Task validation
    TASK_DESCRIPTION_MIN_LENGTH: int = 5
    TASK_DESCRIPTION_MAX_LENGTH: int = 500
    NOTES_MAX_LENGTH: int = 1000
    TECHNICIAN_NAME_MAX_LENGTH: int = 100
    
    # Task type validation
    TASK_TYPE_NAME_MIN_LENGTH: int = 2
    TASK_TYPE_NAME_MAX_LENGTH: int = 100


# ═══════════════════════════════════════════════════════════════════════════
# STATUS AND PRIORITY ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class TaskStatus:
    """Task status constants"""
    PENDING = "pending"
    COMPLETED = "completed"
    
    @classmethod
    def all(cls):
        return [cls.PENDING, cls.COMPLETED]
    
    @classmethod
    def display_names(cls):
        return {
            cls.PENDING: "Εκκρεμής",
            cls.COMPLETED: "Ολοκληρωμένη"
        }


class TaskPriority:
    """Task priority constants"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    @classmethod
    def all(cls):
        return [cls.LOW, cls.MEDIUM, cls.HIGH]
    
    @classmethod
    def display_names(cls):
        return {
            cls.LOW: "Χαμηλή",
            cls.MEDIUM: "Μεσαία",
            cls.HIGH: "Υψηλή"
        }
    
    @classmethod
    def icons(cls):
        return {
            cls.LOW: "🟢",
            cls.MEDIUM: "🟡",
            cls.HIGH: "🔴"
        }


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== Configuration Examples ===\n")
    
    # Window configuration
    print(f"Window size: {UIConfig.WINDOW_WIDTH}x{UIConfig.WINDOW_HEIGHT}")
    print(f"Sidebar width: {UIConfig.SIDEBAR_WIDTH}px")
    
    # Font configuration
    print(f"\nFont family: {FontConfig.FONT_FAMILY}")
    print(f"Base body font size: {FontConfig.FONT_SIZE_BODY}pt")
    
    # Color themes
    print(f"\nDark theme primary bg: {ColorThemes.DARK['bg_primary']}")
    print(f"Light theme primary bg: {ColorThemes.LIGHT['bg_primary']}")
    
    # Validation rules
    print(f"\nGroup name length: {ValidationRules.GROUP_NAME_MIN_LENGTH}-{ValidationRules.GROUP_NAME_MAX_LENGTH}")
    
    # Task enums
    print(f"\nTask statuses: {TaskStatus.all()}")
    print(f"Task priorities: {TaskPriority.all()}")
    print(f"Priority icons: {TaskPriority.icons()}")
