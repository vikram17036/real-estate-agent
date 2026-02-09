# Third-party library imports
from langchain_core.tools import StructuredTool
from typing import List, Optional
from pydantic import BaseModel, Field

# Local application imports
try:
    from src.agent.agent_config import AgentDependencies
    from src.models.customer_profile import (
        CustomerProfile,
        apply_defaults_to_profile,
        normalize_customer_profile,
        validate_customer_profile,
    )
    from src.data.restaurant_data import generate_available_slots, add_mock_reservation, RESTAURANT_HOURS
    from src.utils.restaurant_utils import (
        filter_menu_by_dietary,
        filter_menu_by_category,
        search_menu_items,
        format_time_slots_for_llm,
    )
    from src.utils.time_utils import format_slots_for_llm as format_slots_legacy
except ModuleNotFoundError:
    from agent.agent_config import AgentDependencies
    from models.customer_profile import (
        CustomerProfile,
        apply_defaults_to_profile,
        normalize_customer_profile,
        validate_customer_profile,
    )
    from data.restaurant_data import generate_available_slots, add_mock_reservation, RESTAURANT_HOURS
    from utils.restaurant_utils import (
        filter_menu_by_dietary,
        filter_menu_by_category,
        search_menu_items,
        format_time_slots_for_llm,
    )
    from utils.time_utils import format_slots_for_llm as format_slots_legacy


def create_check_table_availability_tool(agent_deps: AgentDependencies) -> StructuredTool:
    """Create the check_table_availability tool for LangGraph."""
    
    def check_table_availability(
        name: Optional[str] = None,
        phone: Optional[str] = None,
        party_size: Optional[int] = None,
        date_time_preference: Optional[str] = None,
        dietary_restrictions: List[str] = Field(default_factory=list),
        occasion: Optional[str] = None,
        special_requests: List[str] = Field(default_factory=list),
    ) -> dict:
        """Check table availability for a given date/time and party size."""
        from datetime import datetime, timedelta
        import pytz
        from dateparser import parse
        
        profile = CustomerProfile(
            name=name,
            phone=phone,
            party_size=party_size,
            date_time_preference=date_time_preference,
            dietary_restrictions=dietary_restrictions,
            occasion=occasion,
            special_requests=special_requests,
        )
        
        print(f"customer_profile in check_table_availability {profile}")
        
        validation_errors = validate_customer_profile(profile)
        if validation_errors:
            return {"error": validation_errors}
        
        profile_with_defaults = apply_defaults_to_profile(profile)
        normalized_profile = normalize_customer_profile(profile_with_defaults)
        print(f"normalized profile: {normalized_profile}")
        
        agent_timezone = agent_deps.agent_schedule_config.timezone
        tz = pytz.timezone(agent_timezone)
        
        # Parse date/time preference
        date_str = None
        if normalized_profile.date_time_preference:
            # Try to parse the date/time preference
            now = datetime.now(tz)
            parsed_dt = parse(
                normalized_profile.date_time_preference,
                settings={
                    "PREFER_DATES_FROM": "future",
                    "RELATIVE_BASE": now
                }
            )
            
            if parsed_dt:
                if parsed_dt.tzinfo is None:
                    parsed_dt = tz.localize(parsed_dt)
                date_str = parsed_dt.strftime("%Y-%m-%d")
            else:
                # If parsing fails, try to extract just the date part
                date_str = normalized_profile.date_time_preference
        
        if not date_str:
            # Default to tomorrow
            tomorrow = datetime.now(tz) + timedelta(days=1)
            date_str = tomorrow.strftime("%Y-%m-%d")
        
        # Generate available slots
        available_slots = generate_available_slots(
            date_str,
            normalized_profile.party_size,
            agent_timezone
        )
        
        return {
            "date": date_str,
            "party_size": normalized_profile.party_size,
            "available_slots": available_slots
        }
    
    return StructuredTool.from_function(
        func=check_table_availability,
        name="check_table_availability",
        description="Check table availability for a reservation. Use this when the customer has provided their preferences (name, phone, party_size, date_time_preference). Returns available time slots for the requested date."
    )


def create_get_menu_items_tool(agent_deps: AgentDependencies) -> StructuredTool:
    """Create the get_menu_items tool for LangGraph."""
    
    def get_menu_items(
        category: Optional[str] = None,
        dietary_restrictions: List[str] = Field(default_factory=list),
        search_query: Optional[str] = None,
    ) -> dict:
        """Get menu items filtered by category, dietary restrictions, or search query."""
        try:
            from src.data.restaurant_data import MENU_ITEMS
        except ModuleNotFoundError:
            from data.restaurant_data import MENU_ITEMS
        
        menu_items = MENU_ITEMS.copy()
        
        # Filter by category
        if category:
            menu_items = filter_menu_by_category(menu_items, category)
        
        # Filter by dietary restrictions
        if dietary_restrictions:
            menu_items = filter_menu_by_dietary(menu_items, dietary_restrictions)
        
        # Search by query
        if search_query:
            menu_items = search_menu_items(menu_items, search_query)
        
        # Convert to list of dicts for JSON serialization
        return {
            "menu_items": [
                {
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "description": item["description"],
                    "category": item["category"],
                    "price": item["price"],
                    "dietary_info": item["dietary_info"],
                    "allergens": item["allergens"]
                }
                for item in menu_items
            ],
            "count": len(menu_items)
        }
    
    return StructuredTool.from_function(
        func=get_menu_items,
        name="get_menu_items",
        description="Get menu items. Use this when customers ask about the menu, specific dishes, dietary options, or ingredients. You can filter by category (appetizers, mains, desserts, drinks), dietary restrictions (vegan, vegetarian, gluten-free), or search by dish name."
    )


def create_book_table_tool(agent_deps: AgentDependencies) -> StructuredTool:
    """Create the book_table tool for LangGraph."""
    
    def book_table(
        selected_date_time: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        party_size: Optional[int] = None,
        dietary_restrictions: List[str] = Field(default_factory=list),
        occasion: Optional[str] = None,
        special_requests: List[str] = Field(default_factory=list),
    ) -> str:
        """Book a table reservation."""
        from datetime import datetime, timedelta
        import pytz
        from dateparser import parse
        
        profile = CustomerProfile(
            name=name,
            phone=phone,
            party_size=party_size,
            date_time_preference=selected_date_time,
            dietary_restrictions=dietary_restrictions,
            occasion=occasion,
            special_requests=special_requests,
        )
        
        normalized_profile = normalize_customer_profile(profile)
        print(f"customer_profile in book_table {normalized_profile}")
        
        # Validate profile
        validation_errors = validate_customer_profile(normalized_profile)
        if validation_errors:
            return f"Sorry, I need some information: {', '.join(validation_errors)}"
        
        agent_timezone = agent_deps.agent_schedule_config.timezone
        tz = pytz.timezone(agent_timezone)
        now = datetime.now(tz)
        
        # Parse selected date/time
        start_dt = parse(
            selected_date_time,
            settings={
                "PREFER_DATES_FROM": "future",
                "RELATIVE_BASE": now
            }
        )
        
        if not start_dt:
            return "Sorry, I couldn't understand the selected time. Please try again."
        
        # Localize if needed
        if start_dt.tzinfo is None:
            start_dt = tz.localize(start_dt)
        
        # Check if time is in the past
        if start_dt < now:
            return "Sorry, that time is in the past. Please select a future date and time."
        
        # Check if time is within restaurant hours
        restaurant_open = start_dt.replace(hour=RESTAURANT_HOURS["open"], minute=0, second=0, microsecond=0)
        restaurant_close = start_dt.replace(hour=RESTAURANT_HOURS["close"], minute=0, second=0, microsecond=0)
        
        if start_dt < restaurant_open or start_dt >= restaurant_close:
            return f"Sorry, we're only open from {RESTAURANT_HOURS['open']}:00 to {RESTAURANT_HOURS['close']}:00. Please select a time within our hours."
        
        # Create reservation
        reservation_data = {
            "customer_name": normalized_profile.name,
            "phone": normalized_profile.phone,
            "party_size": normalized_profile.party_size,
            "date_time": start_dt.isoformat(),
            "dietary_restrictions": normalized_profile.dietary_restrictions,
            "occasion": normalized_profile.occasion,
            "special_requests": normalized_profile.special_requests,
        }
        
        reservation_id = add_mock_reservation(reservation_data)
        
        # Format confirmation message
        formatted_time = start_dt.strftime("%A, %B %d at %I:%M %p")
        confirmation = (
            f"Perfect! Your reservation is confirmed. "
            f"Reservation ID: {reservation_id}\n"
            f"Name: {normalized_profile.name}\n"
            f"Party Size: {normalized_profile.party_size}\n"
            f"Date & Time: {formatted_time}\n"
        )
        
        if normalized_profile.special_requests:
            confirmation += f"Special Requests: {', '.join(normalized_profile.special_requests)}\n"
        
        confirmation += "We look forward to seeing you!"
        
        return confirmation
    
    return StructuredTool.from_function(
        func=book_table,
        name="book_table",
        description=(
            "Book a table reservation. Always include the selected_date_time along with customer details"
            " (name, phone, party_size). You can also include dietary_restrictions, occasion, and"
            " special_requests if the customer mentioned them."
        )
    )


def get_tools_for_langgraph(agent_deps: AgentDependencies) -> List[StructuredTool]:
    """Get all tools for LangGraph with dependencies injected."""
    return [
        create_check_table_availability_tool(agent_deps),
        create_get_menu_items_tool(agent_deps),
        create_book_table_tool(agent_deps),
    ]

