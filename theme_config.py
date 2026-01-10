"""
Theme Configuration - Dynamic με Settings Support
"""

import customtkinter as ctk
import json
import os

# ═══════════════════════════════════════════════════
# SETTINGS FILE
# ═══════════════════════════════════════════════════

SETTINGS_FILE = "settings.json"

# Default settings
_current_theme_name = "dark"
_current_font_scale = 1.0

# ═══════════════════════════════════════════════════
# THEMES
# ═══════════════════════════════════════════════════

THEMES = {
    "dark": {
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2b2b2b",
        "bg_tertiary": "#3a3a3a",
        "card_bg": "#2b2b2b",
        "card_border": "#454545",
        "card_border2": "#404040",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "text_disabled": "#666666",
        "accent_blue": "#3B8ED0",
        "accent_green": "#28a745",
        "accent_orange": "#ffa500",
        "accent_red": "#dc3545",
        "sidebar_bg": "#1e1e1e",
        "sidebar_hover": "#2d2d2d",
        "royal_purple": "#947AD2"
    },
    "light": {
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
}

# ═══════════════════════════════════════════════════
# BASE FONT SIZES (before scaling)
# ═══════════════════════════════════════════════════

BASE_FONTS = {
    "title": 24,
    "heading": 18,
    "body": 13,
    "input": 15,  # ← ΠΡΟΣΘΗΚΗ!   Νέο μέγεθος για input fields
    "small": 11,
    "tiny": 9
}


# ═══════════════════════════════════════════════════
# SETTINGS MANAGEMENT
# ═══════════════════════════════════════════════════

def load_settings():
    """Φόρτωση settings από JSON"""
    global _current_theme_name, _current_font_scale

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                _current_theme_name = settings.get("theme", "dark")
                _current_font_scale = settings.get("font_scale", 1.0)

                # Validation
                if _current_theme_name not in THEMES:
                    _current_theme_name = "dark"
                if not (0.8 <= _current_font_scale <= 1.5):
                    _current_font_scale = 1.0

        except Exception as e:
            print(f"Error loading settings: {e}")
            save_settings()  # Create default
    else:
        save_settings()  # Create default


def save_settings():
    """Αποθήκευση settings σε JSON"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "theme": _current_theme_name,
                "font_scale": _current_font_scale
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


def get_current_theme_name():
    """Επιστροφή ονόματος theme"""
    return _current_theme_name


def get_current_theme():
    """Επιστροφή theme dictionary"""
    return THEMES[_current_theme_name]


def set_theme(theme_name):
    """Αλλαγή theme"""
    global _current_theme_name
    if theme_name in THEMES:
        _current_theme_name = theme_name
        save_settings()
        return True
    return False


def get_font_scale():
    """Επιστροφή font scale"""
    return _current_font_scale


def set_font_scale(scale):
    """Αλλαγή font scale"""
    global _current_font_scale
    if 0.8 <= scale <= 1.5:
        _current_font_scale = scale
        save_settings()
        return True
    return False


# ═══════════════════════════════════════════════════
# FONT HELPER
# ═══════════════════════════════════════════════════

def get_font(size_key, weight="normal"):
    """
    Επιστροφή scaled font
    size_key: "title", "heading", "body", "small", "tiny"
    weight:  "normal", "bold"
    """
    base_size = BASE_FONTS.get(size_key, 13)
    scaled_size = int(base_size * _current_font_scale)

    return ctk.CTkFont(
        family="Segoe UI",
        size=scaled_size,
        weight=weight
    )


# ═══════════════════════════════════════════════════
# BUTTON STYLES
# ═══════════════════════════════════════════════════

def get_button_style(button_type):
    """
    Επιστροφή button styling με 3D effect
    button_type: "primary", "success", "danger", "secondary", "special"
    """
    theme = get_current_theme()

    styles = {
        "primary": {
            "fg_color": "#454545",
            "hover_color": "#606060",
            "text_color": "#DCDCDC",
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#555555"
        },
        "primary2": {
            "fg_color": theme["accent_blue"],
            "hover_color": "#2d6ca3",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 2,
            "border_color": "#5AA3D9"
        },
        "success": {
            "fg_color": theme["accent_green"],
            "hover_color": "#218838",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 2,
            "border_color": "#4FD664"
        },
        "danger": {
            "fg_color": theme["accent_red"],
            "hover_color": "#bd2130",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 2,
            "border_color": "#FF5A6E"
        },
        "secondary": {
            "fg_color": theme["bg_tertiary"],
            "hover_color": theme["card_border"],
            "text_color": theme["text_primary"],
            "corner_radius": 10,
            "border_width": 2,
            "border_color": theme["card_border"]
        },
        "special": {
            "fg_color": "#6C63FF",
            "hover_color": "#5549CC",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 2,
            "border_color": "#9B93FF"
        },
        "amber_warning": {
            "fg_color": "#C87E2F",
            "hover_color": "#A46626",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 1,
            "border_color": "#E19A4C"
        },
        "royal_purple": {
            "fg_color": "#7B5EC0",
            "hover_color": "#6349A1",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 1,
            "border_color": "#947AD2"
        },
        "graphite_box": {
            "fg_color": "#2B2B2B",
            "hover_color": "#353535",
            "text_color": "#E0E0E0",
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#404040"
        },
        "emerald_success": {
            "fg_color": "#2D8A57",
            "hover_color": "#236942",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 1,
            "border_color": "#3EB489"
        },
        "electric_blue": {
            "fg_color": "#1F6AA5",
            "hover_color": "#144870",
            "text_color": "white",
            "corner_radius": 10,
            "border_width": 1,
            "border_color": "#307EBA"
        },
        "blender_orange": {
            "fg_color": "#E59530",
            "hover_color": "#F5A642",
            "text_color": "#FFFFFF",
            "corner_radius": 4,
            "border_width": 1,
            "border_color": "#B37021"
        },
        "blender_selection": {
            "fg_color": "#ED9D32",
            "hover_color": "#FFB652",
            "text_color": "#1A1A1A",
            "corner_radius": 6,
            "border_width": 2,
            "border_color": "#FFFFFF"
        },
        "soft_white": {
            "fg_color": "5#E5E5E",  # Ένα απαλό, "σπασμένο" λευκό
            "hover_color": "#F2F2F2",  # Σχεδόν λευκό κατά το πέρασμα του ποντικιού
            "text_color": "#1A1A1A",  # Πολύ σκούρο γκρι (όχι μαύρο) για το κείμενο
            "corner_radius": 10,  # Μεγαλύτερη καμπύλη για πιο μοντέρνο look
            "border_width": 1,
            "border_color": "#D1D1D1"  # Διακριτικό περίγραμμα για να μην "χάνεται"
        },
        "muted_white": {
            "fg_color": "#A0A0A0",
            "hover_color": "#C0C0C0",
            "text_color": "#121212",
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#707070"
        },
        "ghost_style": {
            "fg_color": "#454545",
            "hover_color": "#606060",
            "text_color": "#DCDCDC",
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#555555"
        }
    }

    return styles.get(button_type, styles["primary"])


# ═══════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════

# Load settings on module import
load_settings()