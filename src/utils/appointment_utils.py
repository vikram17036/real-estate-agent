# Standard library imports
from datetime import datetime, timedelta

# Third-party library imports
import requests

# Local application imports
try:
    from src.models.property_recommendation import PropertyRecommendation
    from src.models.user_profile import UserProfile
except ModuleNotFoundError:
    from models.property_recommendation import PropertyRecommendation
    from models.user_profile import UserProfile



def send_appointment_to_make(
        profile: UserProfile,
        property: PropertyRecommendation,
        start_dt: datetime,
        end_dt: datetime,
        make_webhook_url: str
        ) -> str:

    # Construct event title and body
    title = f"Showing for {profile.name} ({property.address}, {property.city})"
    description = (
        f"Thank you for scheduling the showing with us. Here are the details: \n\n"
        f"Property ID: {property.listing_id}\n"
        f"User: {profile.name}\n"
        f"Phone: {profile.phone}\n"
        f"Property: {property.address}, {property.city}, {property.state}, {property.zip_code}\n"
        f"Appointment: {start_dt.strftime('%A, %B %d %Y at %I:%M %p')}"
    )

    payload = {
        "mode": "schedule_appointment",
        "listing_id": property.listing_id,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "title": title,
        "description": description,
        "user": {
            "name": profile.name,
            "phone": profile.phone
        }
    }

    print(f"schedule appt payload: {payload}")
    try:
        response = requests.post(make_webhook_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("confirmation_message", "Your appointment has been scheduled.")
    except Exception as e:
        print(f"[schedule_appointment] Failed to call Make webhook: {e}")
        return "There was an issue scheduling the appointment. Please try again later."


def fetch_busy_slots_from_make(
        start_datetime: datetime,
        make_webhook_url: str) -> list[tuple[datetime, datetime]]:
    end_datetime = start_datetime + timedelta(days=1)

    payload = {
        "mode": "get_busy_slots",
        "start": start_datetime.isoformat(),
        "end": end_datetime.isoformat()
    }

    response = requests.post(make_webhook_url, json=payload)
    response.raise_for_status()
    data = response.json()

    calendars = data.get("calendars", {})
    busy_slots = []

    def parse_iso(value: str) -> datetime:
        if not value:
            raise ValueError("Empty ISO datetime string")

        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        return datetime.fromisoformat(value)

    for calendar_id, calendar_data in calendars.items():
        for item in calendar_data.get("busy", []):
            start_raw = item.get("start")
            end_raw = item.get("end")

            try:
                start = parse_iso(start_raw)
                end = parse_iso(end_raw)
            except Exception as exc:
                print(f"[fetch_busy_slots_from_make] Skipping malformed slot ({start_raw}, {end_raw}): {exc}")
                continue

            busy_slots.append((start, end))

    print(f"agent's schedule {busy_slots}")
    return busy_slots





