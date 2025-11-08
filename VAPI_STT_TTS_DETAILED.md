# VAPI STT/TTS Architecture - Detailed Explanation

## 🎯 Key Concept: VAPI Handles ALL Audio Processing

**Your webhook NEVER touches audio files!**

VAPI acts as a complete abstraction layer:
- ✅ Receives audio from phone calls
- ✅ Converts speech → text (STT)
- ✅ Sends ONLY TEXT to your webhook
- ✅ Receives ONLY TEXT from your webhook  
- ✅ Converts text → speech (TTS)
- ✅ Plays audio back to caller

**Your webhook only deals with text messages.**

---

## 📞 Complete Call Flow with STT/TTS

```
┌─────────────────────────────────────────────────────────────────┐
│                    CALLER'S PHONE                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Phone Call (Audio)
                           │ "I'm looking for a condo in Chicago"
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VAPI PLATFORM                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STT (Speech-to-Text) Module                             │  │
│  │  Provider: OpenAI Whisper / Deepgram / AssemblyAI        │  │
│  │                                                           │  │
│  │  Audio Input: [Raw audio stream from phone]              │  │
│  │      ↓                                                    │  │
│  │  Processing: Convert speech to text                      │  │
│  │      ↓                                                    │  │
│  │  Text Output: "I'm looking for a condo in Chicago"        │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│                         │ TEXT (not audio)                      │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Conversation Manager                                    │  │
│  │  - Maintains conversation context                        │  │
│  │  - Formats messages for webhook                          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ HTTP POST Request
                          │ Content-Type: application/json
                          │ 
                          │ {
                          │   "call": {"id": "call-123"},
                          │   "messages": [
                          │     {
                          │       "role": "user",
                          │       "content": "I'm looking for a condo in Chicago"  ← TEXT!
                          │     }
                          │   ],
                          │   "model": "gpt-4",
                          │   ...
                          │ }
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│            YOUR WEBHOOK SERVER (voice_vapi.py)                   │
│                                                                  │
│  • Receives TEXT message (not audio)                            │
│  • Processes with Pydantic AI agent                             │
│  • Returns TEXT response (not audio)                            │
│                                                                  │
│  Response:                                                       │
│  {                                                               │
│    "choices": [{                                                 │
│      "delta": {                                                  │
│        "content": "Great! Let me help you find..."  ← TEXT!      │
│      }                                                           │
│    }]                                                            │
│  }                                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ HTTP Response (SSE Stream)
                       │ Content-Type: text/event-stream
                       │
                       │ data: {"choices":[{"delta":{"content":"Great!..."}}]}
                       │ data: [DONE]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VAPI PLATFORM                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Conversation Manager                                    │  │
│  │  - Receives text response                                │  │
│  │  - Formats for TTS                                       │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│                         │ TEXT (not audio)                      │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TTS (Text-to-Speech) Module                             │  │
│  │  Provider: 11Labs / OpenAI TTS / Azure TTS               │  │
│  │                                                           │  │
│  │  Text Input: "Great! Let me help you find..."            │  │
│  │      ↓                                                    │  │
│  │  Processing: Convert text to speech                      │  │
│  │      ↓                                                    │  │
│  │  Audio Output: [Generated audio stream]                  │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ Audio Stream
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CALLER'S PHONE                               │
│  🔊 Hears: "Great! Let me help you find..."                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Breakdown: STT (Speech-to-Text)

### Where STT Happens
**Location:** Inside VAPI platform (not your server)

### How It Works

1. **Phone Call Audio Capture**
   ```
   Caller speaks → Phone network → VAPI receives audio stream
   ```

2. **STT Provider Processing**
   VAPI uses one of these providers (configured in dashboard):
   - **OpenAI Whisper**: High accuracy, supports multiple languages
   - **Deepgram**: Fast, real-time streaming
   - **AssemblyAI**: Good accuracy, supports custom models
   - **Google Speech-to-Text**: Enterprise-grade
   - **Azure Speech**: Microsoft's solution

3. **Real-time Streaming**
   ```
   Audio chunks → STT API → Text chunks → Aggregated message
   ```

4. **Text Extraction**
   ```python
   # What VAPI does internally (you never see this):
   audio_stream = receive_phone_audio()
   text = stt_provider.transcribe(audio_stream)
   # text = "I'm looking for a condo in Chicago"
   ```

5. **Message Formatting**
   VAPI then formats this into the JSON it sends to your webhook:
   ```json
   {
     "messages": [
       {
         "role": "user",
         "content": "I'm looking for a condo in Chicago"  ← This is what you receive
       }
     ]
   }
   ```

### STT Configuration in VAPI Dashboard

When you create an assistant in VAPI, you configure:
- **Transcriber Provider**: Choose OpenAI Whisper, Deepgram, etc.
- **Language**: English, Spanish, etc.
- **Model**: Specific model variant (e.g., "whisper-1")
- **Punctuation**: Enable/disable
- **Speaker Diarization**: Identify different speakers

**Example Configuration:**
```json
{
  "transcriber": {
    "provider": "openai",
    "model": "whisper-1",
    "language": "en",
    "punctuation": true
  }
}
```

---

## 🔊 Detailed Breakdown: TTS (Text-to-Speech)

### Where TTS Happens
**Location:** Inside VAPI platform (not your server)

### How It Works

1. **Text Response from Your Webhook**
   ```json
   {
     "choices": [{
       "delta": {
         "content": "Great! Let me help you find a condo in Chicago."
       }
     }]
   }
   ```

2. **TTS Provider Processing**
   VAPI uses one of these providers (configured in dashboard):
   - **11Labs**: Natural, expressive voices
   - **OpenAI TTS**: Fast, clear voices
   - **Azure TTS**: Microsoft voices
   - **Google TTS**: Google Cloud voices
   - **PlayHT**: High-quality voices
   - **ElevenLabs**: Custom voice cloning

3. **Voice Synthesis**
   ```python
   # What VAPI does internally (you never see this):
   text = "Great! Let me help you find..."
   audio = tts_provider.synthesize(
     text=text,
     voice_id="selected_voice_id",
     speed=1.0,
     stability=0.5
   )
   # audio = [Generated audio bytes]
   ```

4. **Audio Streaming**
   ```
   Generated audio → Phone network → Caller hears speech
   ```

### TTS Configuration in VAPI Dashboard

When you create an assistant, you configure:
- **Voice Provider**: 11Labs, OpenAI TTS, etc.
- **Voice ID**: Specific voice (e.g., "Rachel", "Adam")
- **Stability**: How consistent the voice is (0.0-1.0)
- **Similarity Boost**: How similar to original voice (0.0-1.0)
- **Speed**: Speech rate (0.25-4.0x)
- **Style**: Emotion/tone (if supported)

**Example Configuration:**
```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.5,
    "similarityBoost": 0.75,
    "speed": 1.0
  }
}
```

---

## 💻 What Your Code Actually Does

Looking at `voice_vapi.py`:

```python
@app.post("/vapi-webhook/chat/completions")
async def vapi_webhook(req: VAPIRequest):
    # 1. VAPI has ALREADY converted speech to text
    #    You receive TEXT, not audio
    user_message = req.messages[-1].content  # ← This is already text!
    
    # 2. Process with your AI agent (text in, text out)
    response = await agent.run(user_message, ...)
    
    # 3. Return TEXT response (VAPI will convert to speech)
    return {
        "choices": [{
            "delta": {
                "content": response.output  # ← This is text, VAPI converts it
            }
        }]
    }
```

**Key Points:**
- ✅ You receive: `"I'm looking for a condo"` (text string)
- ✅ You return: `"Great! Let me help..."` (text string)
- ❌ You never receive: Audio files
- ❌ You never return: Audio files

---

## 🔄 Real-time Streaming Process

### How VAPI Handles Streaming

1. **During Call:**
   ```
   Caller speaks → VAPI continuously transcribes → Sends chunks to webhook
   ```

2. **VAPI's STT Streaming:**
   - Listens to audio in real-time
   - Sends partial transcriptions as user speaks
   - Sends final message when user pauses/finishes

3. **Your Webhook Response:**
   - VAPI expects Server-Sent Events (SSE) format
   - You can stream text back (though current code sends full response)
   - VAPI converts text chunks to speech as they arrive

### Example Streaming Flow

```
Time 0:00 - Caller starts speaking
Time 0:01 - VAPI STT: "I'm looking" → Sends to webhook
Time 0:02 - VAPI STT: "I'm looking for" → Updates webhook
Time 0:03 - Caller pauses
Time 0:04 - VAPI STT: "I'm looking for a condo in Chicago" → Final message to webhook

Your webhook processes → Returns: "Great! Let me help you find..."

Time 0:05 - VAPI TTS: "Great!" → Starts playing to caller
Time 0:06 - VAPI TTS: "Great! Let me help" → Continues playing
Time 0:07 - VAPI TTS: "Great! Let me help you find..." → Completes
```

---

## 🛠️ Technical Details: STT Providers

### OpenAI Whisper (Default)
- **Accuracy**: Very high
- **Latency**: ~2-3 seconds
- **Languages**: 100+ languages
- **Cost**: ~$0.006 per minute
- **Best for**: High accuracy needs

### Deepgram
- **Accuracy**: High
- **Latency**: <1 second (real-time)
- **Languages**: 30+ languages
- **Cost**: ~$0.0043 per minute
- **Best for**: Low latency, real-time apps

### AssemblyAI
- **Accuracy**: High
- **Latency**: ~1-2 seconds
- **Languages**: 100+ languages
- **Cost**: ~$0.00025 per second
- **Best for**: Custom models, speaker diarization

---

## 🎤 Technical Details: TTS Providers

### 11Labs
- **Quality**: Very natural, expressive
- **Latency**: ~1-2 seconds
- **Voices**: 100+ pre-made, custom cloning
- **Cost**: ~$0.30 per 1000 characters
- **Best for**: Natural conversations, character voices

### OpenAI TTS
- **Quality**: Clear, consistent
- **Latency**: <1 second
- **Voices**: 6 pre-made voices
- **Cost**: ~$0.015 per 1000 characters
- **Best for**: Fast, cost-effective

### Azure TTS
- **Quality**: High, professional
- **Latency**: ~1 second
- **Voices**: 400+ voices, 140+ languages
- **Cost**: ~$0.016 per 1000 characters
- **Best for**: Enterprise, multiple languages

---

## 📊 Complete Data Transformation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    CALLER SPEAKS                              │
│  Audio: [Sound waves]                                         │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           VAPI STT (Speech-to-Text)                           │
│  Input:  Audio stream (PCM, WAV, etc.)                        │
│  Process: OpenAI Whisper / Deepgram / etc.                    │
│  Output: Text string                                          │
│  Example: "I'm looking for a condo in Chicago"                │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           HTTP POST to Your Webhook                           │
│  {                                                            │
│    "messages": [{                                             │
│      "role": "user",                                          │
│      "content": "I'm looking for a condo in Chicago"  ← TEXT  │
│    }]                                                         │
│  }                                                            │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           Your Webhook (voice_vapi.py)                        │
│  • Receives: TEXT (user_message)                             │
│  • Processes: Pydantic AI agent                              │
│  • Returns: TEXT (response.output)                            │
│  Example: "Great! Let me help you find a condo..."           │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           HTTP SSE Response                                  │
│  data: {                                                     │
│    "choices": [{                                              │
│      "delta": {                                               │
│        "content": "Great! Let me help..."  ← TEXT            │
│      }                                                        │
│    }]                                                         │
│  }                                                            │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           VAPI TTS (Text-to-Speech)                          │
│  Input:  Text string                                          │
│  Process: 11Labs / OpenAI TTS / etc.                         │
│  Output: Audio stream (MP3, WAV, etc.)                       │
│  Example: [Generated audio bytes]                             │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CALLER HEARS                              │
│  Audio: [Sound waves]                                         │
│  🔊 "Great! Let me help you find a condo..."                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **VAPI is the Audio Layer**
   - Handles all STT (speech → text)
   - Handles all TTS (text → speech)
   - You never touch audio files

2. **Your Webhook is the Text Layer**
   - Receives text messages
   - Processes with AI agent
   - Returns text responses

3. **Separation of Concerns**
   ```
   VAPI = Audio Processing Layer
   Your Webhook = Business Logic Layer
   ```

4. **No Audio Code Needed**
   - No need for audio libraries
   - No need for STT/TTS APIs in your code
   - Just handle text messages

5. **Configuration Happens in VAPI Dashboard**
   - Choose STT provider
   - Choose TTS provider
   - Configure voice settings
   - Your webhook doesn't need to know about these

---

## 💡 Why This Architecture?

**Benefits:**
- ✅ **Simpler**: You focus on business logic, not audio
- ✅ **Scalable**: VAPI handles audio processing at scale
- ✅ **Flexible**: Change STT/TTS providers without code changes
- ✅ **Cost-effective**: VAPI optimizes audio processing costs
- ✅ **Quality**: VAPI uses best-in-class STT/TTS providers

**Your webhook stays simple:**
```python
# That's it! Just text in, text out.
user_text = request.messages[-1].content
response_text = await agent.process(user_text)
return {"content": response_text}
```

---

## 🔧 Configuration Example

**In VAPI Dashboard (Assistant Settings):**
```json
{
  "transcriber": {
    "provider": "openai",
    "model": "whisper-1"
  },
  "voice": {
    "provider": "11labs",
    "voiceId": "Rachel"
  },
  "serverUrl": "https://your-app.com/vapi-webhook/chat/completions"
}
```

**In Your Code (voice_vapi.py):**
```python
# No STT/TTS configuration needed!
# Just handle text messages
@app.post("/vapi-webhook/chat/completions")
async def vapi_webhook(req: VAPIRequest):
    text_input = req.messages[-1].content  # Already text!
    response = await agent.run(text_input)
    return {"content": response.output}  # Return text!
```

That's the beauty of VAPI - it abstracts away all the audio complexity!


