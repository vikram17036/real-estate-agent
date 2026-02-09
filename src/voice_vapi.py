# Standard library imports
import os
import json

# Third-party library imports
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
import uvicorn

try:
    import logfire
    logfire.configure(send_to_logfire='if-token-present')
    LOGFIRE_AVAILABLE = True
except ImportError:
    logfire = None
    LOGFIRE_AVAILABLE = False

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Local application imports
try:
    from src.agent.agent_config import AgentDependencies
    from src.models.agent_schedule_config import AgentScheduleConfig
    from src.agent.realtor_agent_langgraph import get_restaurant_agent
except ModuleNotFoundError:
    from agent.agent_config import AgentDependencies
    from models.agent_schedule_config import AgentScheduleConfig
    from agent.realtor_agent_langgraph import get_restaurant_agent

# Cost tracking not yet implemented for LangGraph
COST_AVAILABLE = False
async def compute_cost(*_, **__):
    return ("0", "0", "0")


# (Logfire already configured above if available)
make_webhook_url = os.getenv("MAKE_WEBHOOK_URL")
agent_timezone = os.getenv("AGENT_TIMEZONE", "America/New_York")
port = int(os.getenv("VAPI_EXPOSE_PORT", 8000))


app = FastAPI(title="Restaurant Reservation Agent API", description="AI-powered restaurant reservation agent for table bookings and menu inquiries")

# Session store for multiple callers
session_store: Dict[str, Dict] = {}

@app.get("/")
async def root():
    return {"message": "Real Estate Agent API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "real-estate-agent"}

class Call(BaseModel):
    id: str
    type: str

class Message(BaseModel):
    role: str
    content: str

class VAPIRequest(BaseModel):
    model: str
    call: Call
    messages: List[Message]
    temperature: float
    max_tokens: int
    metadata: dict
    timestamp: int
    stream: bool

agent_schedule_config = AgentScheduleConfig(
    timezone=agent_timezone
)

agent_dependencies = AgentDependencies(
    make_webhook_url=make_webhook_url,
    agent_schedule_config=agent_schedule_config
    )

@app.post("/vapi-webhook/chat/completions")
async def vapi_webhook(req: VAPIRequest):
    
    session_id = str(req.call.id)
    user_message = req.messages[-1].content

    # Initialize session if it doesn't exist
    if session_id not in session_store:
        # Create agent for this session
        agent = get_restaurant_agent(agent_dependencies)
        session_store[session_id] = {
            "agent": agent,
            "state": {
                "messages": []
            }
        }

    session = session_store[session_id]
    agent = session["agent"]
    state = session["state"]

    # Add user message to state
    state["messages"].append(HumanMessage(content=user_message))
    
    # Invoke the agent
    config = {}
    result = await agent.ainvoke(state, config)
    
    # Update session state
    session["state"] = result
    
    # Extract agent response - find last AIMessage (may not be the last message if tools executed)
    agent_response = ""
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and message.content:
            agent_response = message.content
            break
    
    # Fallback if no AIMessage found
    if not agent_response:
        last_message = result["messages"][-1]
        agent_response = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)

    print(f"Caller [{session_id}]: {user_message}")
    print(f"Agent [{session_id}]: {agent_response}")

    if COST_AVAILABLE:
        prompt_cost, completion_cost, total_cost = await compute_cost()
        print(f"prompt_cost: {prompt_cost}, completion_cost: {completion_cost}, total_cost: {total_cost}")

    final_response = {
        "id": f"chatcmpl-{session_id}",
        "object": "chat.completion.chunk",
        "created": int(req.timestamp / 1000),
        "model": "gpt-4",
        "choices": [
            {
                "delta": {"content": agent_response},
                "index": 0,
                "finish_reason": "stop",
            }
        ]
    }

    async def stream():
        yield f"data: {json.dumps(final_response)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

if __name__ == "__main__":
    uvicorn.run("voice_vapi:app", host="0.0.0.0", port=port, reload=False)
