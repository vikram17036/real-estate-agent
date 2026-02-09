from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TableAvailability(BaseModel):
    date: str
    time_slots: List[str]  # List of available time slots (ISO format)
    party_size: int
    table_id: Optional[str] = None

class MenuItem(BaseModel):
    item_id: str
    name: str
    description: str
    category: str  # appetizers, mains, desserts, drinks
    price: float
    dietary_info: List[str] = []  # vegan, vegetarian, gluten-free, etc.
    allergens: List[str] = []  # nuts, dairy, shellfish, etc.

class Reservation(BaseModel):
    reservation_id: str
    customer_name: str
    phone: str
    party_size: int
    date_time: datetime
    table_id: Optional[str] = None
    special_requests: List[str] = []

def parse_availability_results(availability_data: dict) -> TableAvailability:
    """Parse availability data into TableAvailability object."""
    return TableAvailability(
        date=availability_data.get("date", ""),
        time_slots=availability_data.get("time_slots", []),
        party_size=availability_data.get("party_size", 0),
        table_id=availability_data.get("table_id")
    )
