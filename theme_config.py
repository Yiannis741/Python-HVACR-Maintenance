"""
Theme Configuration System - Phase 2.2
Centralized theme management with dark/light modes and enhanced typography
"""

import customtkinter as ctk

# ==================== APPEARANCE CONFIGURATION ====================

# Set the appearance mode: "dark" or "light"
APPEARANCE_MODE = "dark"

# ==================== TYPOGRAPHY CONFIGURATION ====================

# Primary font with excellent Greek character support
PRIMARY_FONT = "Segoe UI"

# Fallback font for cross-platform compatibility
FALLBACK_FONT = "Arial"

# Font sizes with enhanced readability
FONT_SIZES = {
    "stat_value": 48,   # Large stat values on dashboard
    "title_large": 28,  # Large titles (from 24px)
    "title": 24,        # Section titles (from 20px)
    "subtitle": 18,     # Subtitles (from 16px)
    "heading": 18,      # Headings (increased from 16px)
    "body": 16,         # Body text (increased from 14px)
    "small": 14,        # Small text (increased from 12px)
    "tiny": 12          # Tiny text (increased from 10px)
}

# ==================== COLOR THEMES ====================

DARK_THEME = {
    # Background colors
    "bg_primary": "#1a1a1a",      # Primary background
    "bg_secondary": "#2b2b2b",    # Secondary background (cards, panels)
    "bg_tertiary": "#3a3a3a",     # Tertiary background (hover states)
    
    # Text colors
    "text_primary": "#ffffff",    # Primary text
    "text_secondary": "#b0b0b0",  # Secondary text (descriptions, labels)
    "text_disabled": "#666666",   # Disabled text
    
    # Accent colors
    "accent_blue": "#1f6aa5",     # Primary actions, links
    "accent_green": "#2fa572",    # Success, add actions
    "accent_red": "#c94242",      # Danger, delete actions
    "accent_orange": "#ff9800",   # Warning, pending states
    "accent_purple": "#9c27b0",   # Special features
    
    # Card styling
    "card_bg": "#2b2b2b",
    "card_border": "#3a3a3a",
    "card_hover": "#353535",
    
    # Status colors
    "status_completed": "#2fa572",
    "status_pending": "#ff9800",
    "status_error": "#c94242"
}

LIGHT_THEME = {
    # Background colors
    "bg_primary": "#f5f5f5",      # Primary background
    "bg_secondary": "#ffffff",    # Secondary background (cards, panels)
    "bg_tertiary": "#e0e0e0",     # Tertiary background (hover states)
    
    # Text colors
    "text_primary": "#212121",    # Primary text
    "text_secondary": "#757575",  # Secondary text (descriptions, labels)
    "text_disabled": "#bdbdbd",   # Disabled text
    
    # Accent colors (same as dark for consistency)
    "accent_blue": "#1f6aa5",
    "accent_green": "#2fa572",
    "accent_red": "#c94242",
    "accent_orange": "#ff9800",
    "accent_purple": "#9c27b0",
    
    # Card styling
    "card_bg": "#ffffff",
    "card_border": "#e0e0e0",
    "card_hover": "#f5f5f5",
    
    # Status colors
    "status_completed": "#2fa572",
    "status_pending": "#ff9800",
    "status_error": "#c94242"
}

# ==================== HELPER FUNCTIONS ====================

def get_current_theme():
    """
    Returns the active theme colors based on APPEARANCE_MODE setting.
    
    Returns:
        dict: Dictionary containing all theme colors
    """
    if APPEARANCE_MODE == "dark":
        return DARK_THEME
    else:
        return LIGHT_THEME


def get_font(size_key="body", weight="normal"):
    """
    Creates a CTkFont object with specified size and weight.
    
    Args:
        size_key (str): Key from FONT_SIZES dictionary (e.g., "title", "body", "small")
        weight (str): Font weight - "normal" or "bold"
    
    Returns:
        CTkFont: Configured font object
    """
    size = FONT_SIZES.get(size_key, FONT_SIZES["body"])
    return ctk.CTkFont(family=PRIMARY_FONT, size=size, weight=weight)


def apply_theme():
    """
    Applies the global theme to CustomTkinter.
    Should be called before creating the main application window.
    """
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme("blue")


def get_button_style(button_type="primary"):
    """
    Returns predefined button styling based on button type.
    
    Args:
        button_type (str): Type of button - "primary", "success", "danger", "secondary"
    
    Returns:
        dict: Dictionary with fg_color and hover_color
    """
    theme = get_current_theme()
    
    styles = {
        "primary": {
            "fg_color": theme["accent_blue"],
            "hover_color": _adjust_color(theme["accent_blue"], -20)
        },
        "success": {
            "fg_color": theme["accent_green"],
            "hover_color": _adjust_color(theme["accent_green"], -20)
        },
        "danger": {
            "fg_color": theme["accent_red"],
            "hover_color": _adjust_color(theme["accent_red"], -20)
        },
        "secondary": {
            "fg_color": theme["text_disabled"],
            "hover_color": _adjust_color(theme["text_disabled"], -20)
        },
        "special": {
            "fg_color": theme["accent_purple"],
            "hover_color": _adjust_color(theme["accent_purple"], -20)
        },
        "warning": {
            "fg_color": theme["accent_orange"],
            "hover_color": _adjust_color(theme["accent_orange"], -20)
        }
    }
    
    return styles.get(button_type, styles["primary"])


def get_card_style():
    """
    Returns consistent card styling for the current theme.
    
    Returns:
        dict: Dictionary with card styling properties
    """
    theme = get_current_theme()
    
    return {
        "fg_color": theme["card_bg"],
        "border_color": theme["card_border"],
        "border_width": 1,
        "corner_radius": 10
    }


def _adjust_color(hex_color, adjustment):
    """
    Adjusts a hex color by a given amount (for hover effects).
    
    Args:
        hex_color (str): Hex color string (e.g., "#1f6aa5")
        adjustment (int): Amount to adjust RGB values (-255 to 255)
    
    Returns:
        str: Adjusted hex color string
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = max(0, min(255, r + adjustment))
    g = max(0, min(255, g + adjustment))
    b = max(0, min(255, b + adjustment))
    return f'#{r:02x}{g:02x}{b:02x}'


# ==================== LEGACY COMPATIBILITY ====================

def adjust_color(hex_color, adjustment):
    """
    Public wrapper for _adjust_color for backward compatibility.
    
    Args:
        hex_color (str): Hex color string
        adjustment (int): Amount to adjust RGB values
    
    Returns:
        str: Adjusted hex color string
    """
    return _adjust_color(hex_color, adjustment)
