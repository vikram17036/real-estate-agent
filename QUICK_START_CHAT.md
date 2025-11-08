# Quick Start: Test Agent with Chat

## ✅ What You Need

1. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
2. **Pinecone index with listings** - Run `src/data/load_listings.py` once to populate
3. **Python environment** - With dependencies installed

---

## 🚀 Run in 3 Steps

### Step 1: Create `.env` file

Create a `.env` file in the root directory (`real-estate-agent-main/`):

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-4o-mini
PINECONE_API_KEY=pc-your-key-here
PINECONE_INDEX_NAME=real-estate-listings
AGENT_TIMEZONE=America/Chicago
MAKE_WEBHOOK_URL=https://your-make-webhook-url.com
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-4o-mini
PINECONE_API_KEY=pc-your-key-here
```

### Step 2: Navigate to project

```bash
cd real-estate-agent-main
```

### Step 3: Run chat

```bash
python src/chat.py
```

---

## 💬 Test Conversation

Try this conversation:

```
You: Hi, I'm looking for a condo in Chicago

Agent: [Will ask for your name, then preferences...]

You: My name is John, I want to buy a 2 bedroom condo for 400k

Agent: [Will ask for remaining info: phone, bathrooms, sqft, etc.]

You: [Answer questions]

Agent: [Will recommend properties and ask about scheduling]
```

---

## 🎯 What to Test

1. **Profile Collection** ✅
   - Agent asks for name, phone, preferences
   - Agent collects all required fields

2. **Property Recommendations** ✅
   - Agent queries Pinecone
   - Agent describes properties nicely

3. **Scheduling** (optional)
   - Agent offers to schedule showing
   - Agent checks availability

---

## 🐛 Troubleshooting

**"No module named 'pydantic_ai'"**
```bash
pip install -r requirements.txt
```

**"OPENAI_API_KEY not found"**
- Create `.env` file with your API key

**"Index not found"**
- Pinecone might need listings loaded
- Confirm `PINECONE_INDEX_NAME` exists and contains vectors

**"Agent not responding"**
- Check OpenAI API key is valid
- Check you have API credits

---

## 📝 Exit Chat

Type `exit` or `quit` to end the session and see cost summary.




