import json
import openai
from pinecone import Pinecone
from time import sleep

from dotenv import load_dotenv
import os
from data_config import LISTINGS_DATASET

# Load .env from project root (two levels up from src/data)
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
LISTINGS_DATASET_PATH = os.path.join(script_dir, LISTINGS_DATASET)

openai_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "real-estate-listings")

# Text generation function
def generate_property_text(property_data: dict) -> str:
    parts = []
    parts.append(f"{property_data.get('property_type', 'Property')} for sale")
    if 'bedrooms' in property_data:
        parts.append(f"with {property_data['bedrooms']} bedroom{'s' if property_data['bedrooms'] != 1 else ''}")
    if 'bathrooms' in property_data:
        parts.append(f"and {property_data['bathrooms']} bathroom{'s' if property_data['bathrooms'] != 1 else ''}")
    if 'neighborhood' in property_data:
        parts.append(f"in {property_data['neighborhood']},")
    if 'city' in property_data and 'state' in property_data:
        parts.append(f"{property_data['city']}, {property_data['state']}.")
    if 'price' in property_data:
        parts.append(f"Priced at ${property_data['price']:,}")
    if 'square_feet' in property_data:
        parts.append(f"with {property_data['square_feet']:,} square feet of living space.")
    if 'lot_size' in property_data:
        parts.append(f"The lot size is {property_data['lot_size']} acres.")
    if 'address' in property_data:
        parts.append(f"Located at {property_data['address']}.")
    if 'year_built' in property_data:
        parts.append(f"Built in {property_data['year_built']}.")
    if 'mls_status' in property_data:
        parts.append(f"MLS Status: {property_data['mls_status']}.")
    if 'days_on_market' in property_data:
        parts.append(f"On the market for {property_data['days_on_market']} days.")
    if 'description' in property_data:
        parts.append(property_data['description'])

    return ' '.join(parts)

# OpenAI embedding function
def get_openai_embeddings(texts: list[str]) -> list[list[float]]:
    response = openai.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

# Load listings
with open(LISTINGS_DATASET_PATH, "r") as f:
    listings = json.load(f)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(pinecone_index_name)

# Get embedding dimension (OpenAI text-embedding-3-small has 1536 dimensions)
EMBEDDING_DIMENSION = 1536

# Batch insert
BATCH_SIZE = 100
for i in range(0, len(listings), BATCH_SIZE):
    batch = listings[i:i + BATCH_SIZE]
    documents = [generate_property_text(item) for item in batch]
    ids = [item["listing_id"] for item in batch]
    metadatas = [{k: v for k, v in item.items()} for item in batch]

    try:
        embeddings = get_openai_embeddings(documents)
    except openai.RateLimitError:
        print("[WARNING] Rate limit hit. Waiting and retrying...")
        sleep(20)
        embeddings = get_openai_embeddings(documents)

    # Prepare vectors for Pinecone
    # Pinecone format: list of tuples (id, vector, metadata)
    vectors_to_upsert = [
        {
            "id": listing_id,
            "values": embedding,
            "metadata": metadata
        }
        for listing_id, embedding, metadata in zip(ids, embeddings, metadatas)
    ]
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors_to_upsert)
    print(f"[OK] Inserted {i + len(batch)} of {len(listings)} listings.")
