"""
Mock restaurant data for development and testing.
"""
from typing import List, Dict
from datetime import datetime, timedelta
import pytz

# Mock menu items
MENU_ITEMS = [
    # Appetizers
    {
        "item_id": "app_001",
        "name": "Bruschetta Trio",
        "description": "Three varieties: classic tomato basil, mushroom truffle, and goat cheese with honey",
        "category": "appetizers",
        "price": 14.99,
        "dietary_info": ["vegetarian"],
        "allergens": ["gluten", "dairy"]
    },
    {
        "item_id": "app_002",
        "name": "Caesar Salad",
        "description": "Crisp romaine lettuce with house-made caesar dressing, parmesan, and croutons",
        "category": "appetizers",
        "price": 12.99,
        "dietary_info": ["vegetarian"],
        "allergens": ["dairy", "eggs", "gluten"]
    },
    {
        "item_id": "app_003",
        "name": "Shrimp Scampi",
        "description": "Succulent shrimp sautéed in garlic butter and white wine",
        "category": "appetizers",
        "price": 16.99,
        "dietary_info": [],
        "allergens": ["shellfish", "dairy"]
    },
    {
        "item_id": "app_004",
        "name": "Caprese Salad",
        "description": "Fresh mozzarella, tomatoes, and basil with balsamic glaze",
        "category": "appetizers",
        "price": 13.99,
        "dietary_info": ["vegetarian", "gluten-free"],
        "allergens": ["dairy"]
    },
    
    # Main Courses
    {
        "item_id": "main_001",
        "name": "Grilled Salmon",
        "description": "Atlantic salmon with lemon herb butter, served with roasted vegetables and quinoa",
        "category": "mains",
        "price": 28.99,
        "dietary_info": ["gluten-free"],
        "allergens": ["fish"]
    },
    {
        "item_id": "main_002",
        "name": "Ribeye Steak",
        "description": "12oz prime ribeye, cooked to perfection, with garlic mashed potatoes and seasonal vegetables",
        "category": "mains",
        "price": 34.99,
        "dietary_info": ["gluten-free"],
        "allergens": []
    },
    {
        "item_id": "main_003",
        "name": "Vegetarian Risotto",
        "description": "Creamy arborio rice with seasonal vegetables, parmesan, and truffle oil",
        "category": "mains",
        "price": 22.99,
        "dietary_info": ["vegetarian", "gluten-free"],
        "allergens": ["dairy"]
    },
    {
        "item_id": "main_004",
        "name": "Chicken Parmesan",
        "description": "Breaded chicken breast with marinara sauce and melted mozzarella, served with pasta",
        "category": "mains",
        "price": 24.99,
        "dietary_info": [],
        "allergens": ["gluten", "dairy", "eggs"]
    },
    {
        "item_id": "main_005",
        "name": "Vegan Buddha Bowl",
        "description": "Quinoa, roasted vegetables, chickpeas, avocado, and tahini dressing",
        "category": "mains",
        "price": 19.99,
        "dietary_info": ["vegan", "gluten-free"],
        "allergens": []
    },
    
    # Desserts
    {
        "item_id": "dessert_001",
        "name": "Chocolate Lava Cake",
        "description": "Warm chocolate cake with a molten center, served with vanilla ice cream",
        "category": "desserts",
        "price": 9.99,
        "dietary_info": ["vegetarian"],
        "allergens": ["gluten", "dairy", "eggs"]
    },
    {
        "item_id": "dessert_002",
        "name": "Tiramisu",
        "description": "Classic Italian dessert with espresso-soaked ladyfingers and mascarpone",
        "category": "desserts",
        "price": 8.99,
        "dietary_info": ["vegetarian"],
        "allergens": ["gluten", "dairy", "eggs"]
    },
    {
        "item_id": "dessert_003",
        "name": "Fresh Fruit Plate",
        "description": "Seasonal fresh fruits with mint and honey drizzle",
        "category": "desserts",
        "price": 7.99,
        "dietary_info": ["vegan", "gluten-free"],
        "allergens": []
    },
    
    # Drinks
    {
        "item_id": "drink_001",
        "name": "House Wine Selection",
        "description": "Red, white, or rosé wine by the glass",
        "category": "drinks",
        "price": 8.99,
        "dietary_info": ["vegan", "gluten-free"],
        "allergens": []
    },
    {
        "item_id": "drink_002",
        "name": "Craft Cocktail",
        "description": "Signature cocktails made with premium spirits and fresh ingredients",
        "category": "drinks",
        "price": 12.99,
        "dietary_info": ["vegan", "gluten-free"],
        "allergens": []
    },
    {
        "item_id": "drink_003",
        "name": "Fresh Lemonade",
        "description": "House-made lemonade with fresh lemons",
        "category": "drinks",
        "price": 4.99,
        "dietary_info": ["vegan", "gluten-free"],
        "allergens": []
    }
]

# Restaurant configuration
RESTAURANT_HOURS = {
    "open": 11,  # 11 AM
    "close": 22,  # 10 PM
    "timezone": "America/New_York"
}

# Mock reservations storage (in production, this would be a database)
_mock_reservations: List[Dict] = []

def generate_available_slots(date_str: str, party_size: int, timezone_str: str = "America/New_York") -> List[str]:
    """
    Generate mock available time slots for a given date and party size.
    
    Args:
        date_str: Date in ISO format or "YYYY-MM-DD"
        party_size: Number of people
        timezone_str: Timezone string
        
    Returns:
        List of available time slots in ISO format
    """
    tz = pytz.timezone(timezone_str)
    
    # Parse date
    try:
        if "T" in date_str:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        # If parsing fails, use today
        date_obj = datetime.now(tz).date()
    
    # Get restaurant hours
    open_hour = RESTAURANT_HOURS["open"]
    close_hour = RESTAURANT_HOURS["close"]
    
    # Generate time slots (every 30 minutes)
    available_slots = []
    start_time = datetime.combine(date_obj, datetime.min.time().replace(hour=open_hour, minute=0))
    end_time = datetime.combine(date_obj, datetime.min.time().replace(hour=close_hour, minute=0))
    
    # Localize to timezone
    start_time = tz.localize(start_time)
    end_time = tz.localize(end_time)
    
    current = start_time
    slot_interval = timedelta(minutes=30)
    
    # Filter out slots that are too close to closing time (need at least 1.5 hours)
    while current + timedelta(hours=1.5) <= end_time:
        # Check if this slot conflicts with existing reservations
        slot_conflicts = False
        for reservation in _mock_reservations:
            res_start = reservation.get("date_time")
            if isinstance(res_start, str):
                res_start = datetime.fromisoformat(res_start)
            if isinstance(res_start, datetime):
                res_start = tz.localize(res_start) if res_start.tzinfo is None else res_start.astimezone(tz)
                res_end = res_start + timedelta(hours=2)  # Assume 2-hour reservations
                
                # Check for overlap
                if current < res_end and current + timedelta(hours=2) > res_start:
                    slot_conflicts = True
                    break
        
        if not slot_conflicts:
            available_slots.append(current.isoformat())
        
        current += slot_interval
    
    # Limit to top 6 slots for simplicity
    return available_slots[:6]

def add_mock_reservation(reservation_data: Dict) -> str:
    """Add a mock reservation and return confirmation ID."""
    reservation_id = f"RES-{len(_mock_reservations) + 1:04d}"
    reservation_data["reservation_id"] = reservation_id
    _mock_reservations.append(reservation_data)
    return reservation_id

def get_mock_reservations() -> List[Dict]:
    """Get all mock reservations."""
    return _mock_reservations
