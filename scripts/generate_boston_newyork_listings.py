from __future__ import annotations

import json
import random
from pathlib import Path


BOSTON_NEIGHBORHOODS = [
    "Back Bay",
    "Beacon Hill",
    "South End",
    "North End",
    "Charlestown",
    "Fenway",
    "Allston",
    "Jamaica Plain",
    "Dorchester",
    "Seaport",
]

NYC_NEIGHBORHOODS = [
    "Upper East Side",
    "Upper West Side",
    "Chelsea",
    "Greenwich Village",
    "SoHo",
    "Harlem",
    "Tribeca",
    "Brooklyn Heights",
    "Williamsburg",
    "Long Island City",
]

PROPERTY_TYPES = ["Condo", "Single Family", "Multi-Family", "Townhouse", "Co-op"]
MLS_STATUSES = ["active", "pending", "coming soon"]
STREET_NAMES = [
    "Commonwealth Ave",
    "Boylston St",
    "Massachusetts Ave",
    "Lexington Ave",
    "Madison Ave",
    "Fulton St",
    "Atlantic Ave",
    "Broadway",
    "Main St",
    "Garden St",
]


def make_listing(
    prefix: str,
    idx: int,
    *,
    city: str,
    state: str,
    neighborhoods: list[str],
    lat_base: float,
    lon_base: float,
    zip_start: int,
    zip_end: int,
) -> dict:
    random.seed(f"{prefix}-{idx}")

    neighborhood = random.choice(neighborhoods)
    price = random.randint(450_000, 2_500_000)
    property_type = random.choice(PROPERTY_TYPES)
    bedrooms = random.randint(1, 5)
    bathrooms = round(random.uniform(1, 4), 1)
    square_feet = random.randint(650, 4_200)
    lot_size = round(random.uniform(0.02, 0.3), 2) if property_type != "Condo" else 0.0
    year_built = random.randint(1890, 2023)
    days_on_market = random.randint(0, 120)

    latitude = round(lat_base + random.uniform(-0.05, 0.05), 6)
    longitude = round(lon_base + random.uniform(-0.05, 0.05), 6)

    address = f"{random.randint(120, 9999)} {random.choice(STREET_NAMES)}"
    zip_code = str(random.randint(zip_start, zip_end)).zfill(5)

    description = (
        f"Stylish {property_type.lower()} in the heart of {neighborhood}, {city}. "
        f"Features {bedrooms} bedrooms, {bathrooms} baths, and {square_feet:,} sq ft. "
        "Updated kitchen, generous natural light, and proximity to transit, dining, and parks. "
        "Ideal for modern city living."
    )

    return {
        "listing_id": f"{prefix}{idx:04d}",
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "neighborhood": neighborhood,
        "latitude": latitude,
        "longitude": longitude,
        "price": price,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "square_feet": square_feet,
        "lot_size": lot_size,
        "year_built": year_built,
        "days_on_market": days_on_market,
        "description": description,
        "mls_status": random.choice(MLS_STATUSES),
    }


def build_dataset() -> list[dict]:
    listings: list[dict] = []

    for i in range(1, 51):
        listings.append(
            make_listing(
                "BOS",
                i,
                city="Boston",
                state="MA",
                neighborhoods=BOSTON_NEIGHBORHOODS,
                lat_base=42.3601,
                lon_base=-71.0589,
                zip_start=2101,
                zip_end=2199,
            )
        )

    for i in range(1, 51):
        listings.append(
            make_listing(
                "NYC",
                i,
                city="New York",
                state="NY",
                neighborhoods=NYC_NEIGHBORHOODS,
                lat_base=40.7128,
                lon_base=-74.0060,
                zip_start=10001,
                zip_end=11697,
            )
        )

    return listings


def main() -> None:
    output_path = Path("src/data/boston_newyork_listings.json")
    listings = build_dataset()
    output_path.write_text(json.dumps(listings, indent=2))
    print(f"Wrote {len(listings)} listings to {output_path}")


if __name__ == "__main__":
    main()

