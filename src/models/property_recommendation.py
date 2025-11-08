from pydantic import BaseModel
from typing import List

class PropertyRecommendation(BaseModel):
    listing_id: str
    address: str
    neighborhood: str
    city: str
    state: str
    zip_code: str
    price: int
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: float
    year_built: int
    property_type: str
    mls_status: str
    days_on_market: int
    latitude: float
    longitude: float
    description: str

def parse_pinecone_results(pinecone_results: dict) -> List[PropertyRecommendation]:
    """
    Parse Pinecone query results into PropertyRecommendation objects.
    
    Pinecone returns results in format:
    {
        'matches': [
            {
                'id': 'listing_id',
                'score': 0.95,
                'metadata': {...},
                'values': [...]  # embedding vector
            }
        ]
    }
    """
    recommendations = []
    
    if 'matches' not in pinecone_results:
        return recommendations
    
    for match in pinecone_results['matches']:
        meta = match.get('metadata', {})
        
        # Convert metadata values to proper types
        recommendation = PropertyRecommendation(
            listing_id=str(meta.get("listing_id", "")),
            address=str(meta.get("address", "")),
            city=str(meta.get("city", "")),
            state=str(meta.get("state", "")),
            zip_code=str(meta.get("zip_code", "")),
            neighborhood=str(meta.get("neighborhood", "")),
            property_type=str(meta.get("property_type", "")),
            bedrooms=int(meta.get("bedrooms", 0)),
            bathrooms=float(meta.get("bathrooms", 0)),
            square_feet=int(meta.get("square_feet", 0)),
            lot_size=float(meta.get("lot_size", 0)),
            price=int(meta.get("price", 0)),
            year_built=int(meta.get("year_built", 0)),
            mls_status=str(meta.get("mls_status", "")),
            days_on_market=int(meta.get("days_on_market", 0)),
            latitude=float(meta.get("latitude", 0)),
            longitude=float(meta.get("longitude", 0)),
            description=str(meta.get("description", "")),
        )
        recommendations.append(recommendation)

    return recommendations
