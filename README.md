# 🍽️ Restaurant Reservation AI Voice & Chat Agent

This project is an AI-powered **Restaurant Reservation Agent** capable of handling customer inquiries via **text chat** and **voice (VAPI)**. It uses natural language understanding to collect reservation details, check table availability, answer menu questions, and book table reservations.

---

## ✨ Features

- 🔍 **Understands customer preferences** from natural conversations (party size, date/time, dietary restrictions, etc.)
- 📅 **Checks table availability** and presents available time slots
- 🍽️ **Answers menu questions** about dishes, ingredients, dietary options, and allergens
- 📞 **Voice-ready** via [VAPI](https://vapi.ai/)
- 🧪 **Interactive test chat CLI** via terminal
- 🔄 Integrated with **Make** for real-time calendar access and scheduling (optional)
- 🛡️ **Smart guardrails** that enforce business rules (e.g., time slot selection before booking)

---

## 🗂️ Project Structure

```
restaurant-agent/
├── src/
│   ├── agent/
│   │   ├── realtor_agent_langgraph.py      # LangGraph agent definition with state graph
│   │   ├── agent_config.py                 # System prompt, agent dependencies
│   │   └── tools/                          # Agent tools (LangChain structured tools)
│   │       ├── langgraph_tools.py          # LangChain structured tools for the agent
│   │       ├── check_table_availability    # Check available time slots
│   │       ├── get_menu_items              # Get menu information
│   │       └── book_table                  # Book reservations
│   │
│   ├── models/                             # Pydantic data models
│   │   ├── customer_profile.py
│   │   ├── restaurant_models.py
│   │   └── agent_schedule_config.py
│   │
│   ├── utils/                              # Support logic
│   │   ├── restaurant_utils.py
│   │   ├── time_utils.py
│   │   └── appointment_utils.py
│   │
│   ├── data/                               # Data loading scripts
│   │   ├── restaurant_data.py
│   │   └── data_config.py
│   │
│   ├── chat.py                             # CLI-based text chat interface
│   └── voice_vapi.py                       # FastAPI server for VAPI webhook
│
├── scripts/                                # Utility scripts
│   └── debug_pinecone_query.py
│
├── requirements.txt                        # Python dependencies
└── .env                                    # Environment variables (not checked in)
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/restaurant-agent.git
cd restaurant-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the root directory with the following variables:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_LLM_MODEL=gpt-4o-mini

# Optional
AGENT_TIMEZONE=America/New_York
MAKE_WEBHOOK_URL=https://your-make-webhook-url.com
VAPI_EXPOSE_PORT=8000
```

**Minimum required variables:**
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

**Note:** The agent uses mock restaurant data by default. No external database setup is required for basic functionality.

---

## 💬 Run Chat (Text Interface)

```bash
python .\src\chat.py
```

This launches a terminal-based chatbot you can interact with using natural language.

---

## 📞 Run Voice Agent (VAPI Webhook)

```bash
python .\src\voice_vapi.py
```

- Exposes a FastAPI webhook on `http://localhost:8000/vapi-webhook/chat/completions`
- Configure VAPI to send POST requests to this endpoint during live calls

---

## 📦 Core Technologies

| Layer | Tool |
|-------|------|
| **LLM Agent Framework** | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| **LLM Provider** | OpenAI (GPT-4o-mini, GPT-4) |
| **Voice Integration** | [VAPI](https://vapi.ai/) |
| **Scheduling Backend** | [Make](https://www.make.com/) (optional) |
| **Environment Handling** | `python-dotenv` |
| **Web Framework** | FastAPI |
| **Observability** | `logfire` |
| **Data Storage** | Mock data (in-memory) |

---

## 🧠 Agent Architecture

The agent is built using **LangGraph**, a stateful agent framework that provides explicit control flow and guardrails. The agent uses a **state graph** with semantic nodes and conditional routing.

### Graph Structure

The agent consists of the following nodes:

1. **`collect_preferences`** - Main conversation node that collects customer preferences and decides when to call tools
2. **`execute_tools`** - Executes LangChain structured tools after validation
3. **`handle_validation_failure`** - Provides customer feedback when business rules are violated
4. **`track_reservation_selection`** - Manages state for selected time slots

### Agent Tools

The agent has access to three tools:

1. **`check_table_availability`** - Checks available time slots for a given date/time and party size
2. **`get_menu_items`** - Retrieves menu items filtered by category, dietary restrictions, or search query
3. **`book_table`** - Books table reservations with customer details

### Guardrails

The agent enforces business rules through explicit validation:

- **Booking guardrail**: Prevents booking reservations unless availability has been checked AND the customer has explicitly selected a time slot
- **Profile validation**: Ensures complete customer profile before checking availability
- **Tool call validation**: Validates all tool calls before execution

### State Management

The agent maintains state across conversations:
- **Messages**: Full conversation history (automatically managed by LangGraph)
- **Selected Time Slot**: Tracks which time slot the customer wants to book (for booking guardrail)
- **Last Available Slots**: Caches the latest available time slots so customers can say "the first one" or reference a time without repeating details

The agent is defined in `src/agent/realtor_agent_langgraph.py` and used in both `chat.py` and `voice_vapi.py`.

---

## ✅ Sample Conversation

**Customer**: I'd like to make a reservation for tomorrow evening  
**Agent**: Great! I'd be happy to help you make a reservation. How many people will be in your party?  
**Customer**: 4 people  
**Agent**: Perfect! And what time would you prefer?  
**Customer**: Around 7pm  
**Agent**: Let me check our availability... I have tables available at 6:30 PM, 7:00 PM, and 7:30 PM. Which works best for you?

---

## 🧪 Testing & Debugging

### Chat Interface

Test the agent interactively:

```bash
python src/chat.py
```

Try conversations like:
- "I'd like to make a reservation for 4 people tomorrow at 7pm"
- "Do you have any vegetarian options?"
- "What's on your menu?"

### Testing Guardrails

Test the booking guardrail:
1. Ask to book a table without checking availability first
2. The agent should check availability and present options
3. Try to book without selecting a time slot
4. The agent should ask which time slot you prefer

### Debugging

- Check console output for tool calls and validation decisions
- Logs (via `logfire`) can be configured using `LOGFIRE_PROJECT_ID` and token in your `.env`

---

## 🔧 How It Works

### Reservation Flow

1. Customer provides preferences → Agent extracts `CustomerProfile` (name, phone, party size, date/time)
2. Agent calls `check_table_availability` → Mock availability system generates available time slots
3. Available time slots returned (e.g., ["2024-01-27T18:00:00", "2024-01-27T19:30:00"])
4. Agent presents options naturally to customer
5. Customer selects a time slot
6. Agent calls `book_table` → Creates reservation → Returns confirmation

### Menu Inquiry Flow

1. Customer asks about menu (e.g., "Do you have vegetarian options?")
2. Agent calls `get_menu_items` with dietary restrictions filter
3. Menu items filtered and returned
4. Agent describes dishes naturally to customer

### Guardrails in Action

The agent explicitly validates tool calls before execution:
- **Before booking**: Checks if availability was checked AND customer selected a time slot
- **Before checking availability**: Validates customer profile completeness (in tool itself)
- **On validation failure**: Routes to `handle_validation_failure` node for customer clarification

---

## 🛠 Future Enhancements (Ideas)

- Real-time reservation system integration (OpenTable, Resy, etc.)
- Persistent customer profiles / conversation memory across sessions
- Support for multiple restaurants or restaurant chains
- Frontend dashboard or mobile interface
- Integration with POS systems for menu updates
- Enhanced guardrails for complex scenarios (large parties, special events)
- Waitlist management for fully booked times

---

## 📄 License

MIT License — free to use and modify for your own restaurant or voice automation projects.
