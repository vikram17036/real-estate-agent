# VAPI Assistant Setup Guide

## Overview: How VAPI Works with This Project

VAPI (Voice API) is a platform that handles:
- **Phone calls** (incoming/outgoing)
- **Voice-to-text** conversion
- **Text-to-speech** generation
- **Call management** (recording, voicemail detection, etc.)

Your application provides the **AI brain** via webhook.

---

## The Two Components

### 1. VAPI Assistant (Created in VAPI Dashboard)

**Where:** Configured at [vapi.ai](https://vapi.ai) dashboard

**What it does:**
- Receives phone calls
- Converts speech to text
- Sends conversation to your webhook
- Converts text responses back to speech
- Handles the phone call flow

**Key Settings:**
- **Voice Model**: Which voice to use (e.g., 11Labs, OpenAI TTS)
- **LLM Model**: Which model VAPI uses (can be overridden by webhook)
- **System Prompt**: Initial instructions (can be overridden by webhook)
- **Webhook URL**: Points to your FastAPI server
- **First Message**: What the assistant says when call starts

### 2. Your Webhook Server (`voice_vapi.py`)

**Where:** Your FastAPI application running on your server

**What it does:**
- Receives POST requests from VAPI with conversation data
- Processes the message using your Pydantic AI agent
- Returns the agent's response in VAPI-compatible format
- Manages conversation sessions per call

**Endpoint:** `POST /vapi-webhook/chat/completions`

---

## Step-by-Step Setup Process

### Step 1: Deploy Your Webhook Server

1. **Start your FastAPI server:**
   ```bash
   python src/voice_vapi.py
   ```
   Or deploy to a cloud service (AWS, Railway, Render, etc.)

2. **Get your public URL:**
   - Local development: Use ngrok or similar tunneling service
   - Production: Use your deployed domain
   - Example: `https://your-app.railway.app/vapi-webhook/chat/completions`

### Step 2: Create VAPI Assistant in Dashboard

1. **Go to** [vapi.ai dashboard](https://dashboard.vapi.ai)
2. **Create New Assistant**
3. **Configure:**

   **Basic Settings:**
   - Name: "Real Estate Agent"
   - First Message: "Hi! I'm your virtual real estate assistant..."
   
   **Model Settings:**
   - Provider: OpenAI
   - Model: gpt-4 (or your preferred model)
   - Temperature: 0.3
   
   **Voice Settings:**
   - Provider: 11Labs (or OpenAI TTS)
   - Voice: Choose a professional voice
   
   **Webhook Settings:**
   - Server URL: `https://your-domain.com/vapi-webhook/chat/completions`
   - Method: POST
   - Include conversation history: Yes

### Step 3: Export Assistant Configuration (Optional)

**Why export?**
- Version control
- Backup configuration
- Share with team
- Recreate easily

**How to export:**
1. In VAPI dashboard, go to your assistant
2. Look for "Export" or "Download" option
3. Save as JSON file (e.g., `vapi_assistant_config.json`)

**Note:** The project includes a sample `vapi_assistant_config.json` showing the expected structure.

### Step 4: Test the Integration

1. **Get a phone number** from VAPI
2. **Assign it to your assistant**
3. **Make a test call**
4. **Check logs** in your FastAPI server to see requests

---

## How Data Flows

```
┌─────────────┐
│  Caller    │
│  Phones    │
│  VAPI #    │
└─────┬───────┘
      │
      ▼
┌─────────────────────────────────────┐
│         VAPI Platform               │
│  • Receives call                    │
│  • Converts speech → text           │
│  • Sends to your webhook            │
│  • Converts text → speech           │
│  • Plays to caller                  │
└─────┬───────────────────────────────┘
      │
      │ POST /vapi-webhook/chat/completions
      │ {
      │   "call": { "id": "call-123" },
      │   "messages": [...],
      │   "model": "gpt-4",
      │   ...
      │ }
      │
      ▼
┌─────────────────────────────────────┐
│    Your FastAPI Server              │
│    (voice_vapi.py)                  │
│                                     │
│  • Receives request                 │
│  • Extracts user message            │
│  • Runs Pydantic AI agent           │
│  • Returns response                 │
│                                     │
└─────┬───────────────────────────────┘
      │
      │ Response: SSE stream
      │ {
      │   "choices": [{
      │     "delta": {"content": "..."}
      │   }]
      │ }
      │
      ▼
┌─────────────────────────────────────┐
│         VAPI Platform               │
│  • Receives response                │
│  • Converts to speech               │
│  • Plays to caller                  │
└─────────────────────────────────────┘
```

---

## Request/Response Format

### What VAPI Sends to Your Webhook

```json
{
  "model": "gpt-4",
  "call": {
    "id": "call-abc123",
    "type": "inboundPhoneCall"
  },
  "messages": [
    {
      "role": "user",
      "content": "I'm looking for a 2-bedroom condo in Chicago"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 500,
  "metadata": {},
  "timestamp": 1234567890,
  "stream": true
}
```

### What Your Webhook Returns

Your server returns Server-Sent Events (SSE) format:

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567,"model":"gpt-4","choices":[{"delta":{"content":"Great! Let me help you find..."},"index":0,"finish_reason":null}]}

data: [DONE]
```

---

## Key Configuration Points

### In VAPI Dashboard:
- ✅ **Webhook URL**: Must point to your deployed server
- ✅ **First Message**: What assistant says when call starts
- ✅ **Voice**: Choose professional, friendly voice
- ✅ **Model**: Can use any OpenAI model (your webhook can override)

### In Your Code (`voice_vapi.py`):
- ✅ **Session Management**: Tracks each call separately
- ✅ **Message History**: Maintains conversation context
- ✅ **Response Format**: Must match VAPI's expected SSE format
- ✅ **Agent Integration**: Uses your Pydantic AI agent for logic

---

## Important Notes

1. **System Prompt**: 
   - VAPI dashboard has a system prompt field
   - **BUT** your webhook uses the system prompt from `agent_config.py`
   - The webhook's system prompt takes precedence

2. **Model Override**:
   - VAPI dashboard model setting is for fallback
   - Your webhook uses the model from `realtor_agent.py` (OpenAI)

3. **Session Management**:
   - Each call gets a unique `call.id`
   - Your server maintains separate message history per call
   - Sessions stored in memory (lost on server restart)

4. **Streaming**:
   - VAPI expects streaming responses (SSE format)
   - Your server returns streaming format even if not truly streaming

---

## Troubleshooting

### Webhook Not Receiving Requests
- ✅ Check your server is publicly accessible
- ✅ Verify webhook URL in VAPI dashboard
- ✅ Check firewall/security settings
- ✅ Use ngrok for local testing

### Responses Not Working
- ✅ Check response format matches VAPI's expected format
- ✅ Verify SSE headers are correct
- ✅ Check server logs for errors

### No Voice Output
- ✅ Verify VAPI voice settings
- ✅ Check 11Labs/voice provider API keys
- ✅ Test voice in VAPI dashboard

---

## Example: Complete Setup Checklist

- [ ] Deploy `voice_vapi.py` to cloud service
- [ ] Get public URL (e.g., `https://my-app.railway.app`)
- [ ] Create VAPI account
- [ ] Create assistant in VAPI dashboard
- [ ] Configure webhook URL: `https://my-app.railway.app/vapi-webhook/chat/completions`
- [ ] Set voice preferences
- [ ] Get phone number from VAPI
- [ ] Assign number to assistant
- [ ] Test with a phone call
- [ ] Export assistant config as JSON (optional)
- [ ] Monitor logs and costs

---

## Exporting VAPI Assistant Config

**To export from VAPI dashboard:**
1. Go to your assistant
2. Click "Settings" or "..." menu
3. Select "Export" or "Download JSON"
4. Save as `vapi_assistant_config.json`

**To import/restore:**
1. Go to VAPI dashboard
2. Create new assistant
3. Import from JSON file
4. Adjust webhook URL if needed

**Note:** The exported JSON may include:
- Assistant name and settings
- Voice configuration
- Model settings
- Webhook URL
- First message
- Other VAPI-specific settings

But it **won't include**:
- Your FastAPI server code
- Your agent logic
- Your ChromaDB data
- Your Make scenario

Those are separate components that need to be set up independently.


