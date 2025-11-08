# Testing Agent with Chat Interface

## 🎯 Purpose

Use `chat.py` to test your agent's logic **without setting up VAPI/voice**:
- ✅ Test user profile collection
- ✅ Test property recommendations
- ✅ Test scheduling logic
- ✅ Debug agent behavior
- ✅ See agent responses in real-time

---

## 🚀 Quick Start

### Step 1: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Required for chat.py
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_LLM_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo, etc.

# Database configuration
CHROMA_DB_LISTINGS=real_estate_listings

# Optional: Make webhook (for scheduling tests)
MAKE_WEBHOOK_URL=https://your-make-webhook-url.com
AGENT_TIMEZONE=America/Chicago
```

### Step 2: Make Sure ChromaDB is Set Up

The agent needs ChromaDB with property listings. If you haven't loaded data yet:

```bash
# Navigate to data directory
cd src/data

# Load listings (if you have the data file)
python load_listings.py
```

### Step 3: Run Chat Interface

```bash
# From project root
python src/chat.py
```

---

## 💬 Example Chat Session

```
Welcome to the Real Estate Agent Chat!
Agent: Hello! I'm your virtual real estate assistant. How can I help you today?

You: Hi, I'm looking for a condo

Agent: Great! I'd love to help you find a condo. May I know your name?

You: John Smith

Agent: Nice to meet you, John! Are you looking to buy or rent?

You: Buy

Agent: Perfect! And where are you hoping to find this property?

You: Chicago

Agent: Great! I'm curious, are you looking for a house, an apartment, or something else entirely?

You: Condo

Agent: Got it. How many bedrooms are you hoping for, and how many bathrooms?

You: 2 bedrooms and 2 bathrooms

Agent: Perfect. Do you have a budget in mind for this purchase?

You: 400k

Agent: How much space are you looking for, in square feet?

You: Around 1500

Agent: Okay, and what's a good phone number to reach you at so I can follow up?

You: 555-123-4567

Agent: [Agent collects must_haves and good_to_haves...]

Agent: Alright, John, I think I have a really good understanding of what you're looking for. Just one last quick review: You're looking to buy a condo in Chicago with 2 bedrooms, 2 bathrooms, around 1500 square feet, with a budget of $400,000. Does that sound right?

You: Yes

Agent: [Agent calls recommend_properties tool...]
Agent: Okay, I found a charming condo in a great neighborhood! It's located at 123 Main St, Chicago, listed at $385,000 and has two bedrooms and two baths. The kitchen was just renovated, and it has a huge backyard — perfect for summer barbecues! Would you like to schedule a showing?

You: Yes, I'd like to see it

Agent: [Agent calls get_agent_availability tool...]
Agent: Great! I have a few time slots available. Would any of these work for you: [shows available times]

You: Tomorrow at 2pm works

Agent: [Agent calls schedule_appointment tool...]
Agent: Perfect! I've scheduled your showing for tomorrow at 2pm. You'll receive a confirmation message shortly.

You: exit

Goodbye!
prompt_cost: 0.001234, completion_cost: 0.000567, total_cost: 0.001801
```

---

## 🔍 What Gets Tested

### 1. **User Profile Collection**
The agent should collect:
- ✅ Name
- ✅ Phone
- ✅ buyOrRent (buy/rent)
- ✅ Location
- ✅ Property type
- ✅ Square feet
- ✅ Budget
- ✅ Bedrooms
- ✅ Bathrooms
- ✅ Must haves
- ✅ Good to haves

### 2. **Property Recommendations**
The agent should:
- ✅ Call `recommend_properties` tool with complete profile
- ✅ Return matching properties from ChromaDB
- ✅ Describe properties in friendly, conversational tone

### 3. **Scheduling (Optional)**
If Make webhook is configured:
- ✅ Check agent availability
- ✅ Schedule appointments
- ✅ Handle date/time preferences

---

## 🐛 Debugging Tips

### Check Agent Logs
The chat interface prints:
- User messages
- Agent responses
- Tool calls (check console output)
- Cost tracking

### Common Issues

**1. ChromaDB not found:**
```
Error: Collection 'real_estate_listings' not found
```
**Solution:** Load listings data first with `load_listings.py`

**2. OpenAI API key missing:**
```
Error: OPENAI_API_KEY environment variable not set
```
**Solution:** Create `.env` file with your OpenAI API key

**3. No properties found:**
```
Agent: I couldn't find any properties matching your criteria.
```
**Solution:** 
- Check if ChromaDB has data loaded
- Verify search criteria aren't too restrictive
- Check `recommend_properties.py` tool for filter logic

**4. Agent not collecting profile:**
```
Agent: Keeps asking same questions repeatedly
```
**Solution:** 
- Check `agent_config.py` system prompt
- Verify UserProfile model in `models/user_profile.py`
- Check tool implementations

---

## 📊 Understanding the Output

### Cost Tracking
At the end of the session, you'll see:
```
prompt_cost: 0.001234     # Cost for input tokens
completion_cost: 0.000567  # Cost for output tokens
total_cost: 0.001801       # Total cost
request_tokens: 1234       # Input tokens used
response_tokens: 567       # Output tokens generated
total_tokens: 1801         # Total tokens
requests: 5                # Number of API calls
```

### Message History
The agent maintains conversation context:
- All previous messages are stored
- Agent remembers what user said earlier
- Context is used for natural follow-up questions

---

## 🎯 Testing Checklist

Use this checklist to verify agent functionality:

- [ ] Agent greets user appropriately
- [ ] Agent asks for name
- [ ] Agent asks for phone number
- [ ] Agent asks buy or rent
- [ ] Agent asks for location
- [ ] Agent asks for property type
- [ ] Agent asks for bedrooms/bathrooms
- [ ] Agent asks for budget
- [ ] Agent asks for square feet
- [ ] Agent asks for must-haves/good-to-haves
- [ ] Agent summarizes profile before recommending
- [ ] Agent calls `recommend_properties` tool
- [ ] Agent describes properties conversationally
- [ ] Agent offers to schedule showing
- [ ] Agent checks availability (if Make configured)
- [ ] Agent schedules appointment (if Make configured)

---

## 🔄 Iterative Testing

### Test Different Scenarios

1. **Complete Profile:**
   ```
   Provide all info at once: "I'm John, 555-1234, looking to buy a 2-bedroom condo in Chicago for $400k"
   ```

2. **Partial Profile:**
   ```
   Provide info gradually and let agent ask questions
   ```

3. **Edge Cases:**
   ```
   - Very high/low budget
   - Unusual property types
   - Missing required fields
   - Invalid phone numbers
   ```

4. **Scheduling:**
   ```
   - Test different date formats
   - Test availability checking
   - Test appointment booking
   ```

---

## 💡 Pro Tips

1. **Start Simple:**
   - Test basic profile collection first
   - Then test recommendations
   - Finally test scheduling

2. **Check Console Output:**
   - Look for tool call logs
   - Check for errors
   - Monitor token usage

3. **Modify System Prompt:**
   - Edit `agent_config.py` to change agent behavior
   - Test different tones/personalities
   - Adjust conversation flow

4. **Test Tools Individually:**
   - You can test tools separately if needed
   - Check `agent/tools/` directory
   - Modify tool logic as needed

---

## 🚀 Next Steps

Once chat interface works:
1. ✅ Agent collects profile correctly
2. ✅ Agent recommends properties
3. ✅ Agent handles scheduling

Then you can:
- Set up VAPI for voice integration
- Deploy webhook server
- Test with real phone calls

---

## 📝 Quick Reference

**Run chat:**
```bash
python src/chat.py
```

**Exit chat:**
```
Type "exit" or "quit"
```

**Required files:**
- `.env` with API keys
- `chroma_db/` with loaded listings
- `src/agent/` with agent code

**Key files to modify:**
- `src/agent/agent_config.py` - System prompt
- `src/models/user_profile.py` - Profile structure
- `src/agent/tools/` - Tool implementations


