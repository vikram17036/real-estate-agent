"""
Restaurant-specific utility functions.
"""
from typing import List, Dict
from datetime import datetime
import json

try:
    from src.data.restaurant_data import MENU_ITEMS, generate_available_slots, RESTAURANT_HOURS
except ModuleNotFoundError:
    from data.restaurant_data import MENU_ITEMS, generate_available_slots, RESTAURANT_HOURS


def filter_menu_by_dietary(menu_items: List[Dict], restrictions: List[str]) -> List[Dict]:
    """
    Filter menu items by dietary restrictions.
    
    Args:
        menu_items: List of menu item dictionaries
        restrictions: List of dietary restrictions (e.g., ["vegan", "gluten-free"])
        
    Returns:
        Filtered list of menu items
    """
    if not restrictions:
        return menu_items
    
    restrictions_lower = [r.lower() for r in restrictions]
    filtered = []
    
    for item in menu_items:
        item_dietary = [d.lower() for d in item.get("dietary_info", [])]
        
        # Check if item matches any of the restrictions
        if any(restriction in item_dietary for restriction in restrictions_lower):
            filtered.append(item)
    
    return filtered


def filter_menu_by_category(menu_items: List[Dict], category: str) -> List[Dict]:
    """Filter menu items by category."""
    if not category:
        return menu_items
    
    category_lower = category.lower()
    return [item for item in menu_items if item.get("category", "").lower() == category_lower]


def search_menu_items(menu_items: List[Dict], search_query: str) -> List[Dict]:
    """Search menu items by name or description."""
    if not search_query:
        return menu_items
    
    query_lower = search_query.lower()
    results = []
    
    for item in menu_items:
        name_match = query_lower in item.get("name", "").lower()
        desc_match = query_lower in item.get("description", "").lower()
        
        if name_match or desc_match:
            results.append(item)
    
    return results


def format_time_slots_for_llm(slots: List[str], tz_str: str = "America/New_York") -> str:
    """
    Format time slots for LLM consumption.
    
    Args:
        slots: List of ISO format datetime strings
        tz_str: Timezone string
        
    Returns:
        JSON string with formatted slots
    """
    import pytz
    from datetime import datetime
    
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    current_time = now.strftime("%A, %B %d at %I:%M %p %Z")
    
    formatted_slots = []
    for iso in slots:
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            else:
                dt = dt.astimezone(tz)
            
            formatted_time = dt.strftime("%A, %B %d at %I:%M %p").lstrip("0")
            formatted_slots.append(formatted_time)
        except Exception as e:
            print(f"Error formatting slot {iso}: {e}")
            continue
    
    output = {
        "current_time": current_time,
        "available_slots": formatted_slots,
        "slot_count": len(formatted_slots)
    }
    
    return json.dumps(output, indent=2)
