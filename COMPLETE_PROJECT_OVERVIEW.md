# 🏡 Real Estate AI Voice Agent - Complete Project Overview

## 📋 Executive Summary

This is a **production-ready AI-powered Real Estate Voice Agent** that can handle property inquiries via **voice calls** (VAPI) and **text chat**. The agent uses advanced AI to understand natural language, search property listings using vector embeddings, and schedule appointments through calendar integration.

---

## 🎯 What This Project Does

### Core Functionality

1. **Natural Language Understanding**: The agent converses naturally with potential buyers/renters, collecting their preferences through conversation
2. **Property Recommendations**: Uses vector similarity search to find matching properties from a database of listings
3. **Appointment Scheduling**: Integrates with calendar systems (via Make) to check availability and book property showings
4. **Multi-Modal Interface**: Works via voice calls (VAPI) and text chat (CLI)

### User Flow

1. **User contacts agent** (phone call or chat)
2. **Agent collects preferences**:
   - Name and phone number
   - Buy or rent preference
   - Location (city/neighborhood)
   - Property type (Condo, Single Family, Townhouse, Multi-Family)
   - Budget
   - Bedrooms and bathrooms
   - Square footage
   - Must-haves and nice-to-haves
3. **Agent searches properties** using vector embeddings
4. **Agent recommends properties** one at a time with natural descriptions
5. **User can schedule showings** - agent checks calendar availability and books appointments

---

## 🛠️ Complete Tech Stack

### Core AI & ML Framework

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **AI Agent Framework** | [Pydantic AI](https://github.com/ericmjl/pydantic-ai) | Tool-augmented LLM agent framework |
| **LLM Provider** | OpenAI (GPT-4o-mini, GPT-4) | Language understanding and generation |
| **Embedding Model** | OpenAI `text-embedding-3-small` | Vector embeddings for property search (1536 dimensions) |
| **Vector Database** | Pinecone | Managed vector database for property listings |

### Voice Integration

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Voice Platform** | [VAPI (Voice API)](https://vapi.ai/) | Handles phone calls, speech-to-text, text-to-speech |
| **Webhook Server** | FastAPI | Receives VAPI requests and returns agent responses |
| **Server Framework** | Uvicorn | ASGI server for FastAPI |

### Data & Storage

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Vector Database** | Pinecone | Stores property embeddings and metadata |
| **Data Format** | JSON | Property listings stored as JSON files |
| **Session Management** | In-memory dictionary | Tracks conversation state per call |

### Scheduling & Calendar

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Workflow Automation** | [Make](https://www.make.com/) | Calendar integration and appointment booking |
| **Calendar API** | Via Make webhook | Fetches busy slots and creates appointments |
| **Time Handling** | `pytz`, `dateparser` | Timezone-aware date/time parsing |

### Development & Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.10+ | Core programming language |
| **Web Framework** | FastAPI | REST API for VAPI webhook |
| **Environment Config** | `python-dotenv` | Environment variable management |
| **Observability** | Logfire | Logging and monitoring (optional) |
| **Data Validation** | Pydantic | Type-safe data models |

### Supporting Libraries

- **HTTP Client**: `httpx`, `requests` - API calls to Make
- **Date Parsing**: `dateparser` - Natural language date parsing
- **Timezone**: `pytz` - Timezone handling
- **JSON**: Built-in `json` - Data serialization

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  Voice Call  │              │  Text Chat   │            │
│  │   (VAPI)     │              │   (CLI)      │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                              │                    │
│         └──────────────┬───────────────┘                    │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT LAYER                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Pydantic AI Agent (realtor_agent)          │    │
│  │  - System Prompt (conversation guidelines)        │    │
│  │  - Tool-augmented reasoning                       │    │
│  │  - User profile extraction                        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  recommend   │  │  get_agent   │  │  schedule    │    │
│  │  _properties  │  │ _availability│  │ _appointment  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌──────────────┐ ┌──────────────┐
│   Pinecone     │ │     Make     │ │   OpenAI     │
│  (Vector DB)   │ │  (Calendar)  │ │  (Embedding) │
└────────────────┘ └──────────────┘ └──────────────┘
```

### Data Flow

#### 1. Voice Call Flow (VAPI)

```
Caller → VAPI Platform → Speech-to-Text → POST /vapi-webhook/chat/completions
                                                      ↓
                                    FastAPI Server (voice_vapi.py)
                                                      ↓
                                    Pydantic AI Agent (realtor_agent)
                                                      ↓
                                    Tools (recommend_properties, etc.)
                                                      ↓
                                    Pinecone / Make / OpenAI
                                                      ↓
                                    Agent Response → FastAPI
                                                      ↓
                                    VAPI Platform → Text-to-Speech → Caller
```

#### 2. Property Recommendation Flow

```
User: "I want a 2-bedroom condo in Chicago"
         ↓
Agent extracts UserProfile from conversation
         ↓
recommend_properties tool called
         ↓
UserProfile → profile_to_text() → "Condo, 2 bedroom(s), ..."
         ↓
OpenAI Embedding API → Vector embedding (1536 dimensions)
         ↓
Pinecone Query:
  - Vector similarity search
  - Filters: city, property_type, bedrooms, bathrooms, price, sqft
         ↓
Top 3 matching properties returned
         ↓
Agent describes properties naturally
         ↓
User: "I'd like to see the first one"
         ↓
get_agent_availability tool → Make webhook → Calendar API
         ↓
Available time slots returned
         ↓
User selects time
         ↓
schedule_appointment tool → Make webhook → Calendar event created
```

---

## 📁 Project Structure

```
real-estate-agent-main/
│
├── src/
│   ├── agent/
│   │   ├── realtor_agent.py          # Main Pydantic AI agent definition
│   │   ├── agent_config.py            # System prompt & dependencies
│   │   ├── agent_cost.py             # Cost tracking utilities
│   │   └── tools/                     # Agent tools (LLM-callable functions)
│   │       ├── recommend_properties.py    # Vector search for properties
│   │       ├── get_agent_availability.py  # Calendar availability check
│   │       └── schedule_appointment.py    # Book property showing
│   │
│   ├── models/                        # Pydantic data models
│   │   ├── user_profile.py            # User preferences model
│   │   ├── property_recommendation.py # Property data model
│   │   └── agent_schedule_config.py   # Scheduling configuration
│   │
│   ├── utils/                         # Helper utilities
│   │   ├── embedding_utils.py         # OpenAI embedding functions
│   │   ├── time_utils.py              # Time slot computation
│   │   └── appointment_utils.py       # Make webhook integration
│   │
│   ├── data/                          # Data loading scripts
│   │   ├── load_listings.py           # Load listings into Pinecone
│   │   └── data_config.py             # Data configuration
│   │
│   ├── chat.py                        # CLI text chat interface
│   └── voice_vapi.py                  # FastAPI webhook for VAPI
│
├── n8n/                                # Make scenario configuration (legacy folder name)
│   └── Real_Estate_Agent.json
│
├── requirements.txt                   # Python dependencies
├── env.template                       # Environment variable template
├── .env                               # Your environment variables (not in repo)
│
└── Documentation/
    ├── README.md                      # Main project documentation
    ├── VAPI_SETUP_GUIDE.md           # VAPI integration guide
    ├── PINECONE_SETUP.md              # Pinecone setup instructions
    ├── QUICK_START_CHAT.md            # Quick start guide
    └── TESTING_WITH_CHAT.md           # Testing guide
```

---

## 🔧 Key Components Explained

### 1. Pydantic AI Agent (`realtor_agent.py`)

**What it is**: The core AI agent that handles all conversations.

**Key Features**:
- Uses OpenAI models (configurable via `OPENAI_LLM_MODEL`)
- Temperature: 0.3 (balanced creativity/consistency)
- System prompt defines conversation style and behavior
- Automatically extracts `UserProfile` from conversations
- Can call tools autonomously based on context

**How it works**:
```python
realtor_agent = Agent(
    model=model,                    # OpenAI model name
    system_prompt=SYSTEM_PROMPT,    # Conversation guidelines
    temperature=0.3,                # Response randomness
    deps_type=AgentDependencies,    # Dependency injection
    output_type=str,                # Returns text responses
    instrument=True                 # Enable observability
)
```

### 2. Agent Tools

#### `recommend_properties`
- **Input**: `UserProfile` (extracted from conversation)
- **Process**:
  1. Validates user profile
  2. Applies defaults for missing fields
  3. Normalizes data (phone format, price parsing, etc.)
  4. Converts profile to text query
  5. Generates embedding using OpenAI
  6. Queries Pinecone with filters
  7. Returns top 3 matching properties
- **Output**: List of `PropertyRecommendation` objects

#### `get_agent_availability`
- **Input**: `UserProfile`, optional `date_time_preference` (e.g., "tomorrow", "next Friday")
- **Process**:
  1. Parses natural language date/time
  2. Fetches busy slots from Make scenario
  3. Computes available slots with buffer logic
  4. Formats for LLM consumption
- **Output**: JSON string with available time slots

#### `schedule_appointment`
- **Input**: `UserProfile`, `PropertyRecommendation`, `selected_date_time`
- **Process**:
  1. Parses selected date/time
  2. Creates appointment payload
  3. Sends to Make webhook
  4. Returns confirmation message
- **Output**: Confirmation message string

### 3. Vector Search (Pinecone)

**How property search works**:

1. **Data Loading** (`load_listings.py`):
   - Reads JSON file with property listings
   - Generates text description for each property
   - Creates embeddings using OpenAI `text-embedding-3-small`
   - Uploads to Pinecone with metadata

2. **Query Process**:
   - User preferences → text description
   - Text → embedding vector (1536 dimensions)
   - Pinecone similarity search + filters:
     - City match
     - Property type match
     - Price range (budget ± $50,000)
     - Square footage (sqft ± 300)
     - Bedrooms (≥ user preference)
     - Bathrooms (≥ user preference)
   - Returns top 3 matches by similarity score

3. **Why Vector Search?**
   - Finds semantically similar properties
   - Handles natural language queries
   - Can match on "must-haves" and "good-to-haves" even if not exact

### 4. Voice Integration (VAPI)

**Architecture**:
- VAPI handles all voice infrastructure
- Your server provides AI logic via webhook
- Session management per call ID

**Request Format** (from VAPI):
```json
{
  "model": "gpt-4",
  "call": {"id": "call-123", "type": "inboundPhoneCall"},
  "messages": [{"role": "user", "content": "I'm looking for a condo"}],
  "temperature": 0.3,
  "max_tokens": 500,
  "metadata": {},
  "timestamp": 1234567890,
  "stream": true
}
```

**Response Format** (to VAPI):
```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567,"model":"gpt-4","choices":[{"delta":{"content":"Great! Let me help..."},"index":0,"finish_reason":null}]}

data: [DONE]
```

### 5. Calendar Integration (Make)

**Two Modes**:

1. **Get Busy Slots** (`mode: "get_busy_slots"`):
   - Input: Start/end datetime
   - Returns: List of busy time slots from calendar
   - Used by `get_agent_availability` to compute free slots

2. **Schedule Appointment** (`mode: "schedule_appointment"`):
   - Input: User profile, property, start/end time
   - Creates calendar event
   - Returns confirmation message

**Buffer Logic**:
- 2-hour buffer between appointments
- Respects work hours (configurable)
- 30-minute appointment slots

---

## 🔄 Data Models

### UserProfile
```python
class UserProfile:
    name: Optional[str]
    phone: Optional[str]
    buyOrRent: Optional[str]  # "buy" or "rent"
    location: Optional[str]    # City name
    property_type: Optional[str]  # "Condo", "Single Family", etc.
    sqft: Optional[str]
    budget: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    must_haves: List[str]
    good_to_haves: List[str]
```

**Validation**:
- Name: Required, non-empty
- Phone: Required, 10-15 digits
- Location: Required, non-empty
- Budget: Required, numeric
- Property type: Must be one of: Multi-Family, Condo, Single Family, Townhouse
- buyOrRent: Must be "buy" or "rent"

**Normalization**:
- Phone: Formatted to E.164 format (+1XXXXXXXXXX)
- Price: Parses "400k", "400,000", "$400000" → 400000
- Location: Title case
- Defaults applied if missing (e.g., 3 bedrooms, 2 bathrooms)

### PropertyRecommendation
```python
class PropertyRecommendation:
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
```

---

## 🚀 Deployment Architecture

### Development Setup

1. **Local Chat Testing**:
   ```bash
   python src/chat.py
   ```

2. **Voice Webhook Server**:
   ```bash
   python src/voice_vapi.py
   # Runs on http://localhost:8000
   ```

3. **For VAPI Testing** (local):
   - Use ngrok to expose localhost
   - Point VAPI webhook to ngrok URL

### Production Deployment

**Recommended Platforms**:
- **Railway**: Easy Python deployment
- **Render**: Free tier available
- **AWS Lambda**: Serverless option
- **Google Cloud Run**: Container-based
- **Heroku**: Traditional PaaS

**Environment Variables Required**:
```env
# Required
OPENAI_API_KEY=sk-...
OPENAI_LLM_MODEL=gpt-4o-mini
PINECONE_API_KEY=pc-...
PINECONE_INDEX_NAME=real-estate-listings

# Optional
AGENT_TIMEZONE=America/Chicago
MAKE_WEBHOOK_URL=https://your-make-webhook.com
VAPI_EXPOSE_PORT=8000
```

---

## 📊 System Capabilities

### What the Agent Can Do

✅ **Natural Conversation**:
- Understands casual language ("I'm looking for a place", "something around 400k")
- Asks follow-up questions adaptively
- Handles incomplete information gracefully
- Confirms understanding before proceeding

✅ **Intelligent Property Search**:
- Semantic similarity matching
- Multi-criteria filtering (price, size, location, type)
- Returns relevant properties even with partial matches

✅ **Smart Scheduling**:
- Parses natural language dates ("tomorrow", "next Friday")
- Checks real-time calendar availability
- Applies buffer logic to prevent conflicts
- Offers multiple time slots

✅ **Error Handling**:
- Validates user input
- Provides helpful error messages
- Falls back to defaults when appropriate
- Handles API failures gracefully

### Limitations

⚠️ **Current Limitations**:
- Session state lost on server restart (in-memory storage)
- No persistent user profiles
- No multi-language support
- Limited to properties in Pinecone database
- Requires Make for calendar integration (no direct Google Calendar)

---

## 🔐 Security & Privacy

### Data Handling

- **User Data**: Stored in-memory during conversation, not persisted
- **API Keys**: Stored in `.env` file (not committed to repo)
- **Phone Numbers**: Normalized and sent to Make for appointments
- **Property Data**: Public listing information

### Best Practices

- Never commit `.env` file
- Use environment variables for all secrets
- Validate all user input
- Rate limiting recommended for production
- HTTPS required for VAPI webhook

---

## 💰 Cost Considerations

### API Costs

1. **OpenAI**:
   - LLM: ~$0.15-0.60 per 1K tokens (GPT-4o-mini is cheaper)
   - Embeddings: ~$0.02 per 1M tokens
   - Typical conversation: $0.10-0.50

2. **Pinecone**:
   - Free tier: 100K vectors, 100 queries/day
   - Paid: ~$70/month for 1M vectors

3. **VAPI**:
   - Per-minute pricing for phone calls
   - Varies by provider

4. **Make**:
   - Free tier with execution limits
   - Paid plans available

---

## 🧪 Testing

### Chat Interface Testing

```bash
python src/chat.py
```

**Test Scenarios**:
1. Complete user profile collection
2. Property recommendations
3. Availability checking
4. Appointment scheduling
5. Error handling (invalid inputs)

### Voice Testing

1. Deploy webhook server
2. Configure VAPI assistant
3. Make test phone call
4. Monitor logs for errors

---

## 📈 Future Enhancements

### Potential Improvements

- [ ] Persistent user profiles (database)
- [ ] Multi-language support
- [ ] Direct Google Calendar integration
- [ ] Real-time MLS/IDX updates
- [ ] Frontend dashboard
- [ ] Mobile app
- [ ] Multi-agent delegation
- [ ] Sentiment analysis
- [ ] Lead scoring
- [ ] Email follow-ups

---

## 🎓 Learning Resources

### Key Technologies

- **Pydantic AI**: https://github.com/ericmjl/pydantic-ai
- **Pinecone**: https://www.pinecone.io/learn/
- **VAPI**: https://docs.vapi.ai/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Make**: https://www.make.com/en/help

### Concepts to Understand

- **Vector Embeddings**: Converting text to numerical vectors for similarity search
- **RAG (Retrieval-Augmented Generation)**: Using external data to enhance LLM responses
- **Tool-Augmented Agents**: LLMs calling functions to perform actions
- **Session Management**: Maintaining conversation state across requests
- **Webhook Architecture**: Server-to-server communication

---

## 📝 Summary

This is a **production-ready, enterprise-grade AI voice agent** for real estate that:

- ✅ Handles natural conversations via voice and text
- ✅ Uses advanced vector search for property matching
- ✅ Integrates with calendar systems for scheduling
- ✅ Built with modern Python frameworks
- ✅ Scalable architecture (Pinecone, cloud-ready)
- ✅ Well-documented and maintainable

The system demonstrates best practices in:
- AI agent development
- Vector database integration
- Voice platform integration
- Calendar/workflow automation
- Error handling and validation

**Perfect for**: Real estate agencies, property management companies, or as a template for other voice AI applications.

---

*Last Updated: Based on current codebase analysis*
*Tech Stack Version: Python 3.10+, Pydantic AI 0.1.8, Pinecone latest, OpenAI API v1*

