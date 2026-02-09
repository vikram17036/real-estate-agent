# Standard library imports
import json
import os
from typing import TypedDict, Annotated, Sequence, Any, Dict, Optional
from typing_extensions import Literal

# Third-party library imports
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# Local application imports
try:
    from src.agent.agent_config import SYSTEM_PROMPT, AgentDependencies
    from src.agent.tools.langgraph_tools import get_tools_for_langgraph
    from src.models.customer_profile import validate_customer_profile, CustomerProfile
except ModuleNotFoundError:
    from agent.agent_config import SYSTEM_PROMPT, AgentDependencies
    from agent.tools.langgraph_tools import get_tools_for_langgraph
    from models.customer_profile import validate_customer_profile, CustomerProfile

load_dotenv()


class AgentState(TypedDict, total=False):
    """State for the LangGraph agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    selected_time_slot: str  # Time slot the customer chose
    selected_reservation_details: Dict[str, Any]  # Cached reservation details to avoid re-parsing
    last_available_slots: list[str]  # Most recent available time slots returned by the tool


def _extract_available_slots_from_tool_message(msg: ToolMessage) -> list[str]:
    """
    Parse a ToolMessage to extract available time slots (supports stringified JSON or dict payloads).
    """
    content = msg.content

    # ToolMessage.content can be str, dict, list, etc.
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except Exception:
            return []
    else:
        parsed = content

    if isinstance(parsed, dict) and "available_slots" in parsed:
        slots = parsed.get("available_slots") or []
        return slots if isinstance(slots, list) else []

    if isinstance(parsed, list):
        # Some tool runners might return the list directly
        return parsed if all(isinstance(s, str) for s in parsed) else []

    return []


def _pick_time_slot_from_user_message(
    user_message: str, available_slots: list[str]
) -> Optional[str]:
    """
    Heuristically map the user's selection to one of the available time slots.
    Supports time mentions ("7pm", "6:30") and ordinal language ("first slot", "second", etc.).
    """
    if not available_slots:
        return None

    text = user_message.lower()
    
    # Try to parse time from message (e.g., "7pm", "6:30", "7:00")
    import re
    from dateparser import parse
    
    # Try ordinal selection first
    ordinal_map = {
        "first": 0,
        "1st": 0,
        "one": 0,
        "1": 0,
        "second": 1,
        "2nd": 1,
        "two": 1,
        "2": 1,
        "third": 2,
        "3rd": 2,
        "three": 2,
        "3": 2,
        "fourth": 3,
        "4th": 3,
        "four": 3,
        "4": 3,
    }
    for token, idx in ordinal_map.items():
        if token in text and idx < len(available_slots):
            return available_slots[idx]
    
    # Try to match time patterns
    time_patterns = [
        r'\b(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)?\b',
        r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Try to parse the matched time
            for match in matches:
                time_str = ' '.join([m for m in match if m])
                parsed_time = parse(time_str)
                if parsed_time:
                    # Find closest matching slot
                    from datetime import datetime
                    for slot in available_slots:
                        slot_dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
                        if abs((slot_dt.hour * 60 + slot_dt.minute) - (parsed_time.hour * 60 + parsed_time.minute)) < 30:
                            return slot
    
    # Try direct ISO format match
    for slot in available_slots:
        if slot.lower() in text or any(part in text for part in slot.split("T") if "T" in slot):
            return slot
    
    return None


def _update_selection_from_messages(state: AgentState):
    """
    Refresh selection based on the latest human message and cached available slots.
    This keeps guardrails aware of user intent before tool execution.
    """
    slots = state.get("last_available_slots") or []
    if not slots:
        return

    # Find the latest human message
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            selected_slot = _pick_time_slot_from_user_message(msg.content, slots)
            if selected_slot:
                state["selected_time_slot"] = selected_slot
                state["selected_reservation_details"] = {"time_slot": selected_slot}
            return


def validate_tool_calls(state: AgentState) -> Literal["execute_tools", "collect_preferences", "end"]:
    """
    Guardrail function: Validate tool calls before execution.
    
    CRITICAL BUSINESS RULES:
    1. book_table REQUIRES a selected time slot - customer must have chosen a time
       from available slots before booking is allowed.
    2. check_table_availability requires complete customer profile (validated in tool itself)
    
    If validation fails, routes to handle_validation_failure to ask for missing info.
    """
    messages = state["messages"]
    # Ensure selection state is current before validation
    _update_selection_from_messages(state)
    last_message = messages[-1]
    
    # If no tool calls, end
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return "end"
    
    # Check each tool call
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name", "")
        
        # GUARDRAIL: book_table requires a selected time slot
        if tool_name == "book_table":
            # Check if we have a selected time slot in state
            if state.get("selected_time_slot"):
                continue  # Time slot selected, allow booking
            
            # Check message history for availability checks
            # Look for recent availability checks in tool outputs
            has_availability_checked = False
            user_mentioned_time = False
            
            # Check last 15 messages for context
            for msg in reversed(messages[-15:]):
                # Check if availability was checked
                if isinstance(msg, ToolMessage):
                    content_str = str(msg.content).lower()
                    if "available_slots" in content_str or "time_slot" in content_str:
                        has_availability_checked = True
                
                # Check if user mentioned selecting a time
                if isinstance(msg, HumanMessage):
                    content_str = msg.content.lower()
                    # Look for phrases indicating time selection
                    selection_phrases = [
                        "i'd like",
                        "i want",
                        "i'll take",
                        "the first",
                        "the second",
                        "that time",
                        "book",
                        "reserve",
                        "7pm",
                        "6:30",
                        "tomorrow at",
                    ]
                    if any(phrase in content_str for phrase in selection_phrases):
                        user_mentioned_time = True
            
            # Guardrail: Both availability check AND user time selection required
            if not (has_availability_checked and user_mentioned_time):
                print(f"[GUARDRAIL] Blocked book_table: has_availability={has_availability_checked}, user_selected={user_mentioned_time}")
                return "collect_preferences"  # Route to handler to ask which time
    
    # All validations passed, execute tools
    return "execute_tools"


def should_continue(state: AgentState) -> Literal["execute_tools", "handle_validation_failure", "end"]:
    """Check for tool calls, validate them, and route accordingly."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If no tool calls, end
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return "end"
    
    # Validate tool calls using existing validation function
    validation_result = validate_tool_calls(state)
    
    # Map validation results to routing destinations
    if validation_result == "execute_tools":
        return "execute_tools"
    elif validation_result == "collect_preferences":
        return "handle_validation_failure"
    else:
        return "end"


def create_collect_preferences(agent_deps: AgentDependencies):
    """
    Node: collect_preferences
    Collects user preferences through conversation.
    The LLM decides when enough info is gathered to recommend properties.
    """
    def collect_preferences(state: AgentState):
        """Call the LLM model to collect preferences."""
        messages = state["messages"]
        
        # Get the model
        model_name = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
        model = ChatOpenAI(
            model=model_name,
            temperature=0.3,
        )
        
        # Get tools with dependencies (LLM can call recommend_properties when ready)
        tools = get_tools_for_langgraph(agent_deps)
        model_with_tools = model.bind_tools(tools)
        
        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
        # Call the model
        response = model_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    return collect_preferences


def handle_tool_validation_failure(state: AgentState):
    """
    Node: handle_validation_failure
    Handles cases where tool calls fail validation (e.g., booking without time selection).
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Create a clarifying message from the agent
    if hasattr(last_message, 'tool_calls'):
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name", "")
            if tool_name == "book_table":
                slots = state.get("last_available_slots") or []
                if slots:
                    # Format slots for display
                    from datetime import datetime
                    import pytz
                    try:
                        tz = pytz.timezone("America/New_York")  # Default timezone
                        formatted_options = []
                        for idx, slot in enumerate(slots[:6]):
                            try:
                                slot_dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
                                if slot_dt.tzinfo is None:
                                    slot_dt = tz.localize(slot_dt)
                                else:
                                    slot_dt = slot_dt.astimezone(tz)
                                formatted_time = slot_dt.strftime("%I:%M %p")
                                formatted_options.append(f"{idx + 1}) {formatted_time}")
                            except:
                                formatted_options.append(f"{idx + 1}) {slot}")
                        
                        options_str = "; ".join(formatted_options)
                        prompt = (
                            "I'd be happy to book a table for you! Which time slot would you like? "
                            f"Available options: {options_str}. You can say the number or the time."
                        )
                    except Exception as e:
                        prompt = "I'd be happy to book a table for you! Which time slot would you like? Please select from the available times I mentioned."
                else:
                    prompt = "I'd be happy to book a table for you! First, let me check our availability. What date and time are you looking for?"

                clarification = AIMessage(content=prompt)
                return {"messages": [clarification]}
    
    # Default response
    return {"messages": [AIMessage(content="I need a bit more information. Could you clarify what you'd like to do?")]}


def track_reservation_selection(state: AgentState):
    """
    Node: track_reservation_selection
    Extracts and tracks available time slots from tool results for booking guardrail.
    """
    messages = state["messages"]

    # Capture latest available slots from tool outputs
    for msg in reversed(messages[-5:]):
        if isinstance(msg, ToolMessage):
            slots = _extract_available_slots_from_tool_message(msg)
            if slots:
                state["last_available_slots"] = slots
                break

    # Refresh selection using the most recent human turn
    _update_selection_from_messages(state)

    return state


def create_restaurant_agent_graph(agent_deps: AgentDependencies):
    """
    Create and return the LangGraph agent graph with explicit nodes and guardrails.
    
    Graph structure:
    1. collect_preferences -> Validate tool calls
    2. validate_tool_calls -> execute_tools OR collect_preferences OR end
    3. execute_tools -> track_reservation_selection -> collect_preferences
    4. handle_validation_failure -> collect_preferences
    """
    
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Create node functions with dependencies
    collect_preferences_func = create_collect_preferences(agent_deps)
    
    # Add semantic nodes
    graph.add_node("collect_preferences", collect_preferences_func)
    
    # Get tools and create tool execution node
    tools = get_tools_for_langgraph(agent_deps)
    tool_node = ToolNode(tools)
    graph.add_node("execute_tools", tool_node)
    
    # Add validation failure handler
    graph.add_node("handle_validation_failure", handle_tool_validation_failure)
    
    # Add reservation tracking (optional, for state management)
    graph.add_node("track_reservation_selection", track_reservation_selection)
    
    # Set entry point
    graph.set_entry_point("collect_preferences")
    
    # After collecting preferences, validate and route directly (no intermediate node)
    graph.add_conditional_edges(
        "collect_preferences",
        should_continue,  # This now validates AND routes in one step
        {
            "execute_tools": "execute_tools",
            "handle_validation_failure": "handle_validation_failure",
            "end": END,
        },
    )
    
    # After validation failure, go back to collect preferences
    graph.add_edge("handle_validation_failure", "collect_preferences")
    
    # After tools execute, track reservation selection then continue
    graph.add_edge("execute_tools", "track_reservation_selection")
    graph.add_edge("track_reservation_selection", "collect_preferences")
    
    # Compile the graph
    return graph.compile()


def get_restaurant_agent(agent_deps: AgentDependencies):
    """Get a compiled LangGraph agent with dependencies."""
    return create_restaurant_agent_graph(agent_deps)
