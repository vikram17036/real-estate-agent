# VAPI STT/TTS - Code Examples & Data Flow

## 📋 What Data Actually Flows Through

### Example 1: Caller Says "I need a 2-bedroom condo"

#### Step 1: VAPI Receives Audio
```python
# Inside VAPI (you never see this code):
audio_stream = receive_phone_call()  
# audio_stream = [binary audio data: 0x48, 0x65, 0x6c, ...]
```

#### Step 2: VAPI Converts Audio to Text (STT)
```python
# Inside VAPI (you never see this code):
import openai

transcription = openai.audio.transcriptions.create(
    file=audio_stream,
    model="whisper-1"
)
# transcription.text = "I need a 2-bedroom condo"
```

#### Step 3: VAPI Sends TEXT to Your Webhook
```http
POST /vapi-webhook/chat/completions HTTP/1.1
Host: your-server.com
Content-Type: application/json

{
  "model": "gpt-4",
  "call": {
    "id": "call-abc123",
    "type": "inboundPhoneCall"
  },
  "messages": [
    {
      "role": "user",
      "content": "I need a 2-bedroom condo"  ← TEXT, not audio!
    }
  ],
  "temperature": 0.3,
  "max_tokens": 500,
  "metadata": {},
  "timestamp": 1699123456789,
  "stream": true
}
```

#### Step 4: Your Webhook Receives TEXT
```python
# In voice_vapi.py (line 79):
user_message = req.messages[-1].content
# user_message = "I need a 2-bedroom condo"  ← String, not audio!

print(f"Received: {user_message}")
# Output: Received: I need a 2-bedroom condo
```

#### Step 5: Your Agent Processes TEXT
```python
# In voice_vapi.py (line 99-104):
response = await agent.run(
    user_message,  # ← Text input
    deps=deps,
    message_history=message_history,
    usage=usage
)
# response.output = "Great! Let me help you find a 2-bedroom condo in Chicago. What's your budget?"
```

#### Step 6: Your Webhook Returns TEXT
```python
# In voice_vapi.py (line 115-127):
final_response = {
    "id": f"chatcmpl-{session_id}",
    "object": "chat.completion.chunk",
    "created": int(req.timestamp / 1000),
    "model": "gpt-4",
    "choices": [
        {
            "delta": {
                "content": response.output  # ← TEXT response
            },
            "index": 0,
            "finish_reason": "stop",
        }
    ]
}
# Returns: {"choices": [{"delta": {"content": "Great! Let me help..."}}]}
```

#### Step 7: VAPI Receives TEXT Response
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699123456,"model":"gpt-4","choices":[{"delta":{"content":"Great! Let me help you find a 2-bedroom condo in Chicago. What's your budget?"},"index":0,"finish_reason":"stop"}]}

data: [DONE]
```

#### Step 8: VAPI Converts TEXT to Audio (TTS)
```python
# Inside VAPI (you never see this code):
from elevenlabs import generate, play

text = "Great! Let me help you find a 2-bedroom condo in Chicago. What's your budget?"
audio = generate(
    text=text,
    voice="Rachel",
    model="eleven_multilingual_v2"
)
# audio = [binary audio data: 0x52, 0x49, 0x46, ...]
```

#### Step 9: VAPI Plays Audio to Caller
```python
# Inside VAPI (you never see this code):
play_audio_to_phone_call(audio)
# Caller hears: 🔊 "Great! Let me help you find a 2-bedroom condo..."
```

---

## 🔍 Breaking Down Your Actual Code

### What `voice_vapi.py` Actually Does

```python
# ============================================
# YOUR CODE: voice_vapi.py
# ============================================

@app.post("/vapi-webhook/chat/completions")
async def vapi_webhook(req: VAPIRequest):
    # ────────────────────────────────────────
    # 1. Extract TEXT from VAPI request
    #    VAPI has ALREADY done STT conversion
    # ────────────────────────────────────────
    session_id = str(req.call.id)
    user_message = req.messages[-1].content  
    # ↑ This is a STRING, not audio!
    # Example: "I need a 2-bedroom condo"
    
    # ────────────────────────────────────────
    # 2. Process TEXT with your AI agent
    #    Your agent works with text, not audio
    # ────────────────────────────────────────
    response = await agent.run(
        user_message,  # ← Text input
        deps=deps,
        message_history=message_history,
        usage=usage
    )
    # response.output = "Great! Let me help..." (TEXT)
    
    # ────────────────────────────────────────
    # 3. Return TEXT response
    #    VAPI will convert this to audio (TTS)
    # ────────────────────────────────────────
    final_response = {
        "choices": [{
            "delta": {
                "content": response.output  # ← TEXT response
            }
        }]
    }
    
    # Return as SSE stream (text format)
    return StreamingResponse(
        stream(),
        media_type="text/event-stream"
    )
```

**Key Observation:** 
- ❌ No audio processing
- ❌ No STT code
- ❌ No TTS code
- ✅ Only text string handling

---

## 📊 Data Type Comparison

### What VAPI Handles (Audio)
```python
# VAPI internally processes:
audio_stream = bytes([0x52, 0x49, 0x46, 0x46, ...])  # Audio bytes
sample_rate = 16000  # Hz
channels = 1  # Mono
format = "pcm"  # Pulse-code modulation
```

### What Your Webhook Handles (Text)
```python
# Your webhook processes:
user_message = "I need a 2-bedroom condo"  # String
response = "Great! Let me help you..."  # String
```

---

## 🎯 Real Example: Complete Request/Response

### Actual HTTP Request from VAPI
```http
POST /vapi-webhook/chat/completions HTTP/1.1
Host: real-estate-agent.railway.app
Content-Type: application/json
Content-Length: 342

{
  "model": "gpt-4",
  "call": {
    "id": "call-a1b2c3d4",
    "type": "inboundPhoneCall"
  },
  "messages": [
    {
      "role": "system",
      "content": "You are a friendly real estate assistant."
    },
    {
      "role": "user",
      "content": "I'm looking for a 2-bedroom condo in Chicago under 500K"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 500,
  "metadata": {
    "callerId": "+1234567890",
    "callDuration": 15
  },
  "timestamp": 1699123456789,
  "stream": true
}
```

### Your Webhook Processing
```python
# In voice_vapi.py:
req = VAPIRequest(...)  # Parsed from above HTTP request

# Extract text (already converted by VAPI STT)
user_text = req.messages[-1].content
# user_text = "I'm looking for a 2-bedroom condo in Chicago under 500K"

# Process with agent
response = await agent.run(user_text, ...)
# response.output = "Great! I can help you find a 2-bedroom condo in Chicago. Let me search for properties under $500,000. What neighborhood are you interested in?"
```

### Actual HTTP Response to VAPI
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1699123456,"model":"gpt-4","choices":[{"delta":{"content":"Great! I can help you find a 2-bedroom condo in Chicago. Let me search for properties under $500,000. What neighborhood are you interested in?"},"index":0,"finish_reason":"stop"}]}

data: [DONE]
```

### What VAPI Does Next
```python
# Inside VAPI (you never see this):
response_text = "Great! I can help you find a 2-bedroom condo..."

# VAPI converts to audio using TTS
audio = tts_provider.synthesize(
    text=response_text,
    voice="Rachel"
)

# VAPI plays audio to caller
play_audio(audio)
```

---

## 🔄 Streaming Example

### Real-time Streaming Flow

**Caller speaks continuously:**
```
Time 0:00 - Caller: "I'm looking..."
Time 0:01 - VAPI STT: "I'm looking" → Sends partial
Time 0:02 - Caller: "...for a condo..."
Time 0:03 - VAPI STT: "I'm looking for a condo" → Updates
Time 0:04 - Caller: "...in Chicago"
Time 0:05 - Caller pauses (silence)
Time 0:06 - VAPI STT: "I'm looking for a condo in Chicago" → Final message
```

**VAPI sends to your webhook:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I'm looking for a condo in Chicago"
    }
  ]
}
```

**Your webhook processes and responds:**
```json
{
  "choices": [{
    "delta": {
      "content": "Great! Let me help you find a condo in Chicago..."
    }
  }]
}
```

**VAPI TTS streams response:**
```
Time 0:07 - VAPI TTS: "Great!" → Plays to caller
Time 0:08 - VAPI TTS: "Great! Let me help" → Continues
Time 0:09 - VAPI TTS: "Great! Let me help you find..." → Continues
Time 0:10 - VAPI TTS: Complete → Caller hears full response
```

---

## 💡 Key Insight: You Only Deal with Strings

### What You DON'T Need to Handle

```python
# ❌ You DON'T need:
import wave
import pyaudio
import speech_recognition
from pydub import AudioSegment

# ❌ You DON'T process:
audio_bytes = receive_audio()
transcription = stt_model.transcribe(audio_bytes)
audio_output = tts_model.synthesize(text)
```

### What You DO Handle

```python
# ✅ You ONLY need:
# Standard string handling

user_text = request.messages[-1].content  # String
response_text = process_with_ai(user_text)  # String
return {"content": response_text}  # String
```

---

## 🎤 What If You Wanted to Handle Audio Directly?

**If you wanted to handle audio yourself (you don't need to!):**

### Option 1: Direct Audio Processing (Complex)
```python
# You would need to:
# 1. Receive audio from phone
# 2. Convert to text (STT)
# 3. Process with AI
# 4. Convert to audio (TTS)
# 5. Send audio back

# This requires:
- Audio processing libraries
- STT API integration
- TTS API integration
- Real-time streaming
- Audio format conversion
- Error handling for audio issues
```

### Option 2: Use VAPI (What This Project Does - Simple!)
```python
# VAPI handles all audio
# You just handle text

user_text = request.messages[-1].content  # Text
response_text = await agent.run(user_text)  # Text
return {"content": response_text}  # Text
```

**VAPI = Audio abstraction layer**

---

## 📝 Summary Table

| Component | Handles | Your Code? | Example |
|-----------|---------|------------|---------|
| **Phone Call** | Audio stream | ❌ VAPI | `[0x52, 0x49, ...]` |
| **STT** | Audio → Text | ❌ VAPI | `audio → "I need a condo"` |
| **Webhook Input** | Text message | ✅ Your code | `"I need a condo"` |
| **AI Processing** | Text → Text | ✅ Your code | `"I need a condo" → "Great! Let me help..."` |
| **Webhook Output** | Text response | ✅ Your code | `"Great! Let me help..."` |
| **TTS** | Text → Audio | ❌ VAPI | `"Great! Let me help..." → audio` |
| **Phone Output** | Audio stream | ❌ VAPI | `audio → 🔊 Sound` |

**Your webhook only handles the middle part: Text → Text**

---

## 🎯 The Bottom Line

**VAPI = Audio Processing Service**
- Receives audio from phone
- Converts speech to text (STT)
- Sends text to your webhook
- Receives text from your webhook
- Converts text to speech (TTS)
- Plays audio to phone

**Your Webhook = Business Logic Service**
- Receives text messages
- Processes with AI agent
- Returns text responses

**You never touch audio!**

That's why your `voice_vapi.py` is so simple - it's just text processing, not audio processing.


