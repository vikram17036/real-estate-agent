# Standard library imports
import os
import json

# Third-party library imports
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
from pinecone import Pinecone

try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    logfire = None
    LOGFIRE_AVAILABLE = False

from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage

# Local application imports
try:
    from src.agent.agent_config import AgentDependencies
    from src.models.agent_schedule_config import AgentScheduleConfig
    from src.agent.realtor_agent import realtor_agent
except ModuleNotFoundError:
    from agent.agent_config import AgentDependencies
    from models.agent_schedule_config import AgentScheduleConfig
    from agent.realtor_agent import realtor_agent
try:
    from agent.agent_cost import compute_cost
    COST_AVAILABLE = True
except ModuleNotFoundError:
    async def compute_cost(*_, **__):
        return ("0", "0", "0")

    COST_AVAILABLE = False


if LOGFIRE_AVAILABLE:
    logfire.configure(send_to_logfire='if-token-present')

load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "real-estate-listings")
n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
agent_timezone = os.getenv("AGENT_TIMEZONE")
port = int(os.getenv("VAPI_EXPOSE_PORT", 8000))


app = FastAPI(title="Real Estate Agent API", description="AI-powered real estate agent for property recommendations and scheduling")

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

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
pinecone_index = pc.Index(pinecone_index_name)

agent_dependencies = AgentDependencies(
    pinecone_index=pinecone_index,
    pinecone_index_name=pinecone_index_name,
    n8n_webhook_url=n8n_webhook_url,
    agent_schedule_config=agent_schedule_config
    )

@app.post("/vapi-webhook/chat/completions")
async def vapi_webhook(req: VAPIRequest):
    
    session_id = str(req.call.id)
    user_message = req.messages[-1].content

    message_history: List[ModelMessage] = []

    # Initialize session if it doesn't exist
    if session_id not in session_store:
        session_store[session_id] = {
            "agent": realtor_agent,
            "usage": Usage(),
            "agent_dependencies": agent_dependencies,
            "message_history": message_history
        }

    session = session_store[session_id]
    agent = session["agent"]
    usage = session["usage"]
    deps = session["agent_dependencies"]
    message_history = session["message_history"]

    # Run agent (non-streaming)
    response = await agent.run(
        user_message,
        deps=deps,
        message_history=message_history,
        usage=usage
    )

    print(f"Caller [{session_id}]: {user_message}")
    print(f"Agent [{session_id}]: {response.output}")

    if COST_AVAILABLE:
        prompt_cost, completion_cost, total_cost = await compute_cost(usage=usage)
        print(f"prompt_cost: {prompt_cost}, completion_cost: {completion_cost}, total_cost: {total_cost}")

    print(f"request_tokens: {usage.request_tokens}, response_tokens: {usage.response_tokens}, total_tokens: {usage.total_tokens}, requests: {usage.requests}")

    session["message_history"] = response.all_messages()

    final_response = {
        "id": f"chatcmpl-{session_id}",
        "object": "chat.completion.chunk",
        "created": int(req.timestamp / 1000),
        "model": "gpt-4",
        "choices": [
            {
                "delta": {"content": response.output},
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
