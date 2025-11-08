# Third-party library imports
from pydantic_ai import RunContext

# Local application imports
try:
    from src.agent.agent_config import AgentDependencies
    from src.utils.embedding_utils import get_embedding, profile_to_text
    from src.agent.realtor_agent import realtor_agent
    from src.models.property_recommendation import parse_pinecone_results
    from src.models.user_profile import (
        UserProfile,
        apply_defaults_to_profile,
        normalize_user_profile,
        validate_user_profile,
    )
except ModuleNotFoundError:
    from agent.agent_config import AgentDependencies
    from utils.embedding_utils import get_embedding, profile_to_text
    from agent.realtor_agent import realtor_agent
    from models.property_recommendation import parse_pinecone_results
    from models.user_profile import (
        UserProfile,
        apply_defaults_to_profile,
        normalize_user_profile,
        validate_user_profile,
    )


@realtor_agent.tool
async def recommend_properties(
    ctx: RunContext[AgentDependencies],
    profile: UserProfile
) -> dict:

    print(f"user_profile in recommend_properties {profile}")

    validation_errors = validate_user_profile(profile)
    if validation_errors:
        return validation_errors

    user_profile_with_defaults = apply_defaults_to_profile(profile)
    normalized_user_profile = normalize_user_profile(user_profile_with_defaults)
    print(f"normalized profile: {normalized_user_profile}")

    query = profile_to_text(normalized_user_profile)
    query_embedding = get_embedding(query)

    budget_value = int(normalized_user_profile.budget)
    sqft_value = int(normalized_user_profile.sqft)

    price_tolerance = max(int(2 * budget_value), 500000)
    sqft_tolerance = max(int(0.6 * sqft_value), 800)

    pinecone_index = ctx.deps.pinecone_index
    
    # Query Pinecone with filters
    # Pinecone filter format: {"field": {"$operator": value}}
    filter_dict = {
        "$and": [
            {"city": {"$eq": normalized_user_profile.location}},
            {"property_type": {"$eq": normalized_user_profile.property_type}},
            {"square_feet": {"$gte": int(normalized_user_profile.sqft) - sqft_tolerance}},
            {"price": {"$gte": int(normalized_user_profile.budget) - price_tolerance}},
            {"price": {"$lte": int(normalized_user_profile.budget) + price_tolerance}},
            {"bedrooms": {"$gte": int(normalized_user_profile.bedrooms)}},
            {"bathrooms": {"$gte": float(normalized_user_profile.bathrooms)}}
        ]
    }
    
    # Query Pinecone
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter=filter_dict
    )
    
    recommendations = parse_pinecone_results(results)
    return recommendations