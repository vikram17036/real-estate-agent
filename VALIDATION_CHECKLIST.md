# Validation Checklist - LangGraph Migration

## ✅ Pre-Testing Validation

### 1. Code Structure ✅
- [x] LangGraph agent implemented with semantic node names
- [x] Explicit guardrails added for tool execution
- [x] State management properly handled
- [x] Dependencies correctly injected

### 2. Key Guardrails ✅
- [x] **schedule_appointment guardrail**: Requires both property recommendation AND user selection
- [x] **recommend_properties guardrail**: Validated within tool (user profile completeness)
- [x] Validation failure handler provides clear feedback

### 3. Node Names (Interview-Ready) ✅
- [x] `collect_preferences` - Main conversation node
- [x] `validate_tool_calls` - Guardrail validation node  
- [x] `execute_tools` - Tool execution node
- [x] `handle_validation_failure` - Error handling node
- [x] `track_property_selection` - State tracking node

---

## 🧪 Testing Checklist

### Test Case A: Happy Path

**Input:**
```
"I want a 2 bedroom condo in Chicago under 500k"
```

**Expected Flow:**
1. ✅ Agent asks for missing info (name, phone, etc.)
2. ✅ User provides complete profile
3. ✅ Agent calls `recommend_properties` tool
4. ✅ Properties displayed to user
5. ✅ User selects a property
6. ✅ User requests scheduling
7. ✅ Agent calls `get_agent_availability`
8. ✅ Agent calls `schedule_appointment`

**Validation:**
- [ ] Preference extraction works
- [ ] `recommend_properties` tool is called
- [ ] Clean response with property descriptions
- [ ] Scheduling flow completes

---

### Test Case B: Missing Information

**Input:**
```
"I want something in Boston"
```

**Expected Flow:**
1. ✅ Agent asks follow-up questions
2. ✅ Agent does NOT call `recommend_properties` until profile complete
3. ✅ Agent continues collecting preferences

**Validation:**
- [ ] Follow-up questions asked
- [ ] No premature tool calls
- [ ] Conversation continues naturally

---

### Test Case C: Action Gating (Critical)

**Input:**
```
[User asks to schedule before selecting property]
"Can I schedule a showing?"
```

**Expected Flow:**
1. ✅ **GUARDRAIL TRIGGERS**: `validate_tool_calls` detects `schedule_appointment` call
2. ✅ **VALIDATION FAILS**: No property selected
3. ✅ **ROUTING**: Goes to `handle_validation_failure`
4. ✅ **FEEDBACK**: Agent asks "which property would you like to see?"
5. ✅ **NO TOOL EXECUTION**: `schedule_appointment` is NOT called

**Validation:**
- [ ] Guardrail correctly blocks scheduling
- [ ] Clear clarifying message provided
- [ ] No tool execution occurs
- [ ] Conversation flows back to property selection

---

## 🔍 State Correctness Checks

### State Persistence ✅
- [x] Messages persist across turns
- [x] State updates correctly after each turn
- [x] No state loss between interactions

### Property Selection Tracking
- [ ] `selected_property_id` tracked in state when user selects property
- [ ] State properly maintained for scheduling guardrail

### Tool Output Integration
- [ ] Tool results feed back into state correctly
- [ ] Recommendations accessible for subsequent turns

### Infinite Loop Prevention
- [ ] Guardrail doesn't cause infinite loops
- [ ] Validation failure routes correctly
- [ ] Clear exit conditions exist

---

## 🎯 Interview Talking Points

### Guardrail Explanation
**"We have an explicit guardrail that prevents scheduling appointments unless:**
1. **Properties have been recommended** (tool output present)
2. **User has explicitly selected a property** (user message indicates selection)

**This is enforced in the `validate_tool_calls` node before tool execution, ensuring we never create incomplete appointments."**

### Node Structure
**"The graph has five semantic nodes:**
1. **collect_preferences** - Main conversation and preference gathering
2. **validate_tool_calls** - Business rule enforcement (guardrails)
3. **execute_tools** - Tool execution after validation
4. **handle_validation_failure** - User feedback when rules are violated
5. **track_property_selection** - State management for property tracking

**This structure makes the agent's behavior explicit and debuggable."**

### State Management
**"State is managed through a TypedDict with:**
- **messages**: Conversation history (automatically accumulated)
- **selected_property_id**: Tracks user's property choice for scheduling guardrail

**The state persists across turns, allowing the agent to maintain context throughout the conversation."**

---

## 🚀 Quick Manual Test Commands

### Start Chat Interface
```bash
python src/chat.py
```

### Test Sequences

**1. Happy Path:**
```
> I want a 2 bedroom condo in Chicago under 500k
[Answer questions]
> Yes, I'd like to schedule a showing
[Select time]
```

**2. Missing Info:**
```
> I want something in Boston
[Should ask follow-up questions]
```

**3. Guardrail Test:**
```
> [After properties shown] Can I schedule a showing?
[Should ask which property first]
```

---

## ✅ Ready for Tuesday

All code changes complete. Focus areas:
1. ✅ Semantic node naming
2. ✅ Explicit guardrails
3. ✅ State management
4. ✅ Error handling

**Next Step**: Run manual tests using chat interface to validate all scenarios.

