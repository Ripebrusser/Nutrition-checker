"""Formatting utilities for display."""

from typing import Optional, Union

def format_nutrient(value: Optional[float], unit: str = "g", decimals: int = 1) -> str:
    """Format a nutrient value with unit."""
    if value is None:
        return "N/A"
    if decimals == 0:
        return f"{value:.0f} {unit}"
    return f"{value:.{decimals}f} {unit}"

def format_energy(kj: Optional[float], show_kcal: bool = True) -> str:
    """Format energy value in kJ and optionally kcal."""
    if kj is None:
        return "N/A"
    kcal = kj / 4.184
    if show_kcal:
        return f"{kj:.1f} kJ ({kcal:.1f} kcal)"
    return f"{kj:.1f} kJ"

def format_weight(grams: Optional[float]) -> str:
    """Format weight in grams or kg as appropriate."""
    if grams is None:
        return "N/A"
    if grams >= 1000:
        return f"{grams / 1000:.2f} kg"
    return f"{grams:.1f} g"

def format_percentage(value: Optional[float], decimals: int = 1) -> str:
    """Format a decimal as percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"

def format_time_minutes(minutes: Optional[int]) -> str:
    """Format minutes as hours and minutes."""
    if minutes is None or minutes == 0:
        return "N/A"
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}min"

def format_date(date_obj) -> str:
    """Format date for display."""
    if date_obj is None:
        return "N/A"
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%b %d, %Y")
    return str(date_obj)

def format_datetime(dt) -> str:
    """Format datetime for display."""
    if dt is None:
        return "N/A"
    if hasattr(dt, 'strftime'):
        return dt.strftime("%b %d, %Y %H:%M")
    return str(dt)

def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_list(items: list, max_items: int = 5) -> str:
    """Format a list for display."""
    if not items:
        return "None"
    if len(items) <= max_items:
        return ", ".join(str(item) for item in items)
    shown = ", ".join(str(item) for item in items[:max_items])
    remaining = len(items) - max_items
    return f"{shown} (+{remaining} more)"

def format_nutrient_per_serving(value: float, unit: str = "g") -> str:
    """Format nutrient per serving."""
    return f"{value:.1f} {unit}"

def format_meal_slot(slot: str) -> str:
    """Format meal slot for display."""
    mapping = {
        "BREAKFAST": "🌅 Breakfast",
        "MORNING_SNACK": "☕ Morning Snack",
        "LUNCH": "🌞 Lunch",
        "EVENING_SNACK": "🌅 Evening Snack",
        "DINNER": "🌙 Dinner",
    }
    return mapping.get(slot, slot.replace("_", " ").title())

def format_nutrition_status(status: str) -> str:
    """Format nutrition status with color."""
    colors = {
        "COMPLETE": "green",
        "PARTIAL": "orange",
        "UNAVAILABLE": "gray",
        "NO_MAPPED_INGREDIENTS": "red",
    }
    color = colors.get(status, "gray")
    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{status}</span>'

def format_diet_type(diet_type: str) -> str:
    """Format diet type for display."""
    icons = {
        "VEGAN": "🌱 Vegan",
        "VEGETARIAN": "🥦 Vegetarian",
        "EGGETARIAN": "🥚 Eggetarian",
        "NON_VEGETARIAN": "🍗 Non-Vegetarian",
        "JAIN": "🕉️ Jain",
        "PESCATARIAN": "🐟 Pescatarian",
        "FLEXITARIAN": "🌿 Flexitarian",
        "OMNIVORE": "🍽️ Omnivore",
    }
    return icons.get(diet_type, diet_type)

def format_cuisine(cuisine: str) -> str:
    """Format cuisine for display."""
    return cuisine.title() if cuisine else "Unknown"

def format_course(course: str) -> str:
    """Format course for display."""
    return course.title() if course else "Unknown"