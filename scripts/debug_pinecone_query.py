import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone

ROOT_DIR = Path(__file__).resolve().parent.parent

for path in (ROOT_DIR, ROOT_DIR / "src"):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from src.models.user_profile import UserProfile  # type: ignore
from src.utils.embedding_utils import get_embedding, profile_to_text  # type: ignore


def run_debug_query(
    city: str = "Boston",
    property_type: str = "Condo",
    sqft: int = 1000,
    budget: int = 800000,
    bedrooms: int = 2,
    bathrooms: float = 2.0,
    top_k: int = 5,
):
    load_dotenv()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "real-estate-listings"))

    profile = UserProfile(
        city=city,
        location=city,
        property_type=property_type,
        sqft=str(sqft),
        budget=str(budget),
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        must_haves=[],
        good_to_haves=[],
    )

    query = profile_to_text(profile)
    embedding = get_embedding(query)

    price_tolerance = max(int(2 * budget), 500_000)
    sqft_tolerance = max(int(0.6 * sqft), 800)

    filter_dict = {
        "$and": [
            {"city": {"$eq": city}},
            {"property_type": {"$eq": property_type}},
            {"square_feet": {"$gte": sqft - sqft_tolerance}},
            {"price": {"$gte": budget - price_tolerance}},
            {"price": {"$lte": budget + price_tolerance}},
            {"bedrooms": {"$gte": bedrooms}},
            {"bathrooms": {"$gte": bathrooms}},
        ]
    }

    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict,
    )

    print(json.dumps(response.to_dict(), indent=2))


if __name__ == "__main__":
    run_debug_query()

