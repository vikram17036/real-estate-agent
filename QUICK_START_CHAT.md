# Quick Start: Test Agent with Chat

## ✅ What You Need

1. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
2. **ChromaDB with listings** - Already loaded (you have `chroma_db/` folder)
3. **Python environment** - With dependencies installed

---

## 🚀 Run in 3 Steps

### Step 1: Create `.env` file

Create a `.env` file in the root directory (`real-estate-agent-main/`):

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-4o-mini
CHROMA_DB_LISTINGS=real_estate_listings
AGENT_TIMEZONE=America/Chicago
N8N_WEBHOOK_URL=https://your-webhook-url.com
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-4o-mini
CHROMA_DB_LISTINGS=real_estate_listings
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
   - Agent searches ChromaDB
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

**"Collection not found"**
- ChromaDB might need listings loaded
- Check if `chroma_db/` folder exists

**"Agent not responding"**
- Check OpenAI API key is valid
- Check you have API credits

---

## 📝 Exit Chat

Type `exit` or `quit` to end the session and see cost summary.


