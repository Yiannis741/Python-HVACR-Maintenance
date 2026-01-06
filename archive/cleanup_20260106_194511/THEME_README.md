# Phase 2.2 - Dark Theme & Enhanced Typography

## Overview
This update implements a comprehensive dark theme system with enhanced typography for improved readability of Greek characters.

## Screenshot
![Dark Theme Screenshot](screenshot_dark_theme.png)

## Features Implemented

### 1. Theme Configuration System (`theme_config.py`)
- Centralized theme management
- Easy switching between dark and light themes
- Consistent color palette across the application

### 2. Color Palette

#### Dark Theme (Default)
- **Backgrounds:**
  - Primary: `#1a1a1a` - Main window background
  - Secondary: `#2b2b2b` - Sidebar, top bar, and cards
  - Tertiary: `#3a3a3a` - Hover states

- **Text Colors:**
  - Primary: `#ffffff` - Main text
  - Secondary: `#b0b0b0` - Descriptions and labels
  - Disabled: `#666666` - Disabled elements

- **Accent Colors:**
  - Blue `#1f6aa5` - Primary actions
  - Green `#2fa572` - Success actions (New Task)
  - Red `#c94242` - Danger actions (Delete)
  - Orange `#ff9800` - Warning/Pending
  - Purple `#9c27b0` - Special features

#### Light Theme (Alternative)
- Background: `#f5f5f5` primary, `#ffffff` secondary
- Same accent colors for consistency
- Proper contrast for readability

### 3. Enhanced Typography

#### Font Configuration
- **Primary Font:** "Segoe UI" - Excellent Greek character support
- **Fallback Font:** "Arial" - Cross-platform compatibility

#### Font Sizes (Enhanced for Readability)
- **Stat Value:** 48px - Dashboard statistics
- **Title Large:** 28px (from 24px) - Main page titles
- **Title:** 24px (from 20px) - Section titles
- **Subtitle:** 18px (from 16px) - Subtitles
- **Heading:** 16px (from 14px) - Headings
- **Body:** 14px (from 12px) - Body text
- **Small:** 12px (from 11px) - Small text
- **Tiny:** 10px (from 9px) - Tiny text

### 4. Helper Functions

#### `get_current_theme()`
Returns the active theme colors based on the `APPEARANCE_MODE` setting.

```python
theme = theme_config.get_current_theme()
bg_color = theme["bg_primary"]
```

#### `get_font(size_key, weight)`
Creates consistent font objects with specified size and weight.

```python
title_font = theme_config.get_font("title", "bold")
body_font = theme_config.get_font("body")
```

#### `apply_theme()`
Applies global theme settings. Called before creating the main application.

```python
theme_config.apply_theme()
```

#### `get_button_style(type)`
Returns predefined button styling for consistency.

```python
# Available types: "primary", "success", "danger", "secondary", "special", "warning"
style = theme_config.get_button_style("success")
button = ctk.CTkButton(parent, text="Save", **style)
```

#### `get_card_style()`
Returns consistent card styling.

```python
card_style = theme_config.get_card_style()
card = ctk.CTkFrame(parent, **card_style)
```

## Configuration

### Switching Themes
To switch between dark and light themes, edit `theme_config.py`:

```python
# Change this line:
APPEARANCE_MODE = "dark"  # or "light"
```

### Changing Primary Font
To use a different font:

```python
# Change this line:
PRIMARY_FONT = "Segoe UI"  # or "Arial", "Helvetica", "Roboto", etc.
```

## Files Modified

### New Files
- `theme_config.py` - Complete theme configuration system

### Updated Files
- `main.py` - Integrated theme system throughout
  - Updated window configuration
  - Applied theme colors to all frames and labels
  - Updated all font references to use `theme_config.get_font()`
  - Updated all buttons to use `theme_config.get_button_style()`
  
- `ui_components.py` - Updated all components
  - TaskCard - Theme colors and fonts
  - TaskForm - Enhanced typography and button styles
  - UnitsManagement - Consistent styling
  - TaskHistoryView - Theme integration
  - RecycleBinView - Dark theme support
  - TaskRelationshipsView - Updated styling

## UI/UX Improvements

✅ **Dark interface reduces eye strain**
✅ **High contrast for better readability**
✅ **Larger fonts for easier reading of Greek text**
✅ **Consistent button styling across all screens**
✅ **Professional dark theme aesthetic**
✅ **Excellent Greek character rendering with Segoe UI**
✅ **Theme-aware cards and panels**

## Testing

The application has been tested with:
- ✅ Dark theme colors applied correctly
- ✅ Greek characters render properly with "Segoe UI" font
- ✅ All buttons use consistent theme styles
- ✅ All existing features work correctly
- ✅ Font sizes are readable and properly scaled
- ✅ Cards and frames use theme colors

## Compatibility

- **Python:** 3.8+
- **CustomTkinter:** 5.2.2+
- **Platforms:** Windows, Linux, macOS
- **Font Support:** Segoe UI (Windows), Arial (fallback for all platforms)

## Future Enhancements

Potential improvements for future phases:
- Runtime theme switching without restart
- User preference storage in database
- Additional color themes (e.g., blue, green)
- Custom color picker for accent colors
- Theme preview before applying

## Acceptance Criteria - Status

✅ Application starts with dark theme by default
✅ All UI elements use the new fonts and colors
✅ "Segoe UI" font displays Greek characters correctly
✅ Font sizes are increased and readable
✅ Buttons use consistent styles (primary, success, danger)
✅ Users can easily switch to light theme by changing a flag
✅ All existing features work normally with the new theme
✅ Screenshot demonstrates the dark theme implementation

## Credits

Developed for: HVACR Maintenance System v2.0  
Phase: 2.2 - Dark Theme & Enhanced Typography  
Date: January 2026
