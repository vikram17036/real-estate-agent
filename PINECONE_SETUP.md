# Pinecone Setup Guide

## 🎯 Overview

This project now uses **Pinecone** instead of ChromaDB for vector storage. Pinecone is a managed vector database service, so you don't need to install anything locally!

---

## 🚀 Quick Setup

### Step 1: Create Pinecone Account

1. Go to https://www.pinecone.io/
2. Sign up for a free account
3. Get your API key from the dashboard

### Step 2: Create a Pinecone Index

1. In Pinecone dashboard, click "Create Index"
2. Configure:
   - **Index Name**: `real-estate-listings` (or any name you prefer)
   - **Dimensions**: `1536` (OpenAI text-embedding-3-small uses 1536 dimensions)
   - **Metric**: `cosine` (recommended for embeddings)
   - **Pod Type**: `s1.x1` (free tier) or `p1.x1` (paid tier)

### Step 3: Get Your API Key

1. In Pinecone dashboard, go to "API Keys"
2. Copy your API key (starts with something like `pc-...`)

### Step 4: Update `.env` File

Add these to your `.env` file:

```env
PINECONE_API_KEY=pc-your-api-key-here
PINECONE_INDEX_NAME=real-estate-listings
```

---

## 📦 Install Pinecone Client

```bash
pip install pinecone-client
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

---

## 📤 Load Data into Pinecone

Once your index is created and `.env` is configured:

```bash
cd src/data
python load_listings.py
```

This will:
- Load listings from `chicago_listings_1000.json`
- Generate embeddings using OpenAI
- Upload to your Pinecone index

**Note:** This may take a few minutes depending on your data size.

---

## ✅ Verify Setup

### Check if index exists:
```python
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "real-estate-listings"))

# Check index stats
stats = index.describe_index_stats()
print(f"Total vectors: {stats.total_vector_count}")
```

### Test a query:
```python
from utils.embedding_utils import get_embedding

query = "2 bedroom condo in Chicago"
embedding = get_embedding(query)

results = index.query(
    vector=embedding,
    top_k=3,
    include_metadata=True
)

print(f"Found {len(results['matches'])} results")
```

---

## 🔧 Troubleshooting

### "Index not found"
- Make sure you created the index in Pinecone dashboard
- Check that `PINECONE_INDEX_NAME` matches your index name exactly

### "Invalid API key"
- Verify your API key in `.env` file
- Check that API key is active in Pinecone dashboard

### "Dimension mismatch"
- Make sure your index has 1536 dimensions
- OpenAI `text-embedding-3-small` requires 1536 dimensions

### Rate Limits
- Free tier has rate limits
- If you hit limits, wait a bit or upgrade to paid tier

---

## 💰 Pricing

**Free Tier:**
- 1 index
- 100,000 vectors
- 100 queries per day

**Paid Tier:**
- Multiple indexes
- Millions of vectors
- High query throughput

For this project with ~1000 listings, free tier is sufficient!

---

## 🔄 Migration from ChromaDB

If you had data in ChromaDB, you'll need to:
1. Export data from ChromaDB (if you have it)
2. Load it into Pinecone using `load_listings.py`

The old `chroma_db/` folder is no longer needed.

---

## 📝 Environment Variables

Add to `.env`:

```env
# Required
PINECONE_API_KEY=pc-your-key-here
PINECONE_INDEX_NAME=real-estate-listings

# Optional (defaults shown)
# PINECONE_ENVIRONMENT=us-east-1-aws  # Usually auto-detected
```

---

## 🎯 Next Steps

1. ✅ Create Pinecone account
2. ✅ Create index with 1536 dimensions
3. ✅ Add API key to `.env`
4. ✅ Run `load_listings.py` to populate index
5. ✅ Test with `chat.py`

You're ready to go! 🚀




