# Standard library imports
import asyncio
import os

# Third-party library imports
from dotenv import load_dotenv
from pinecone import Pinecone
from typing import List
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage

# Optional imports
try:
    import logfire
    logfire.configure(send_to_logfire='if-token-present')
except ImportError:
    logfire = None

# Local application imports
try:
    from src.agent.realtor_agent import realtor_agent
    from src.agent.agent_config import AgentDependencies
    from src.models.agent_schedule_config import AgentScheduleConfig
except ModuleNotFoundError:
    from agent.realtor_agent import realtor_agent
    from agent.agent_config import AgentDependencies
    from models.agent_schedule_config import AgentScheduleConfig

# Optional cost tracking
try:
    from agent.agent_cost import compute_cost
    COST_TRACKING_AVAILABLE = True
except ImportError:
    COST_TRACKING_AVAILABLE = False

async def main():

    load_dotenv()
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "real-estate-listings")
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    agent_timezone = os.getenv("AGENT_TIMEZONE")
    agent_schedule_config = AgentScheduleConfig(
        timezone=agent_timezone
    ) 

    # Initialize Pinecone
    pc = Pinecone(api_key=pinecone_api_key)
    pinecone_index = pc.Index(pinecone_index_name)

    # Initialize agent and user profile
    agent = realtor_agent
    agent_deps = AgentDependencies(
        pinecone_index=pinecone_index,
        pinecone_index_name=pinecone_index_name,
        n8n_webhook_url=n8n_webhook_url,
        agent_schedule_config=agent_schedule_config
    )

    print("Welcome to the Real Estate Agent Chat!")
    message = "Hello"

    message_history: List[ModelMessage] = []
    agent_usage = Usage()

    # Chat loop
    while True:

        if message.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = await agent.run(
            message, 
            deps=agent_deps,
            message_history=message_history,
            usage=agent_usage
        )
        
        message_history = response.all_messages()
        
        print(f"Agent: {response.output}")

        # Prompt next input
        message = input("You: ")

    if COST_TRACKING_AVAILABLE:
        try:
            prompt_cost, completion_cost, total_cost = await compute_cost(usage=agent_usage)
            print(f"prompt_cost: {prompt_cost}, completion_cost: {completion_cost}, total_cost: {total_cost}")
        except Exception as e:
            print(f"Cost tracking unavailable: {e}")
    
    print(f"request_tokens: {agent_usage.request_tokens}, response_tokens: {agent_usage.response_tokens}, total_tokens: {agent_usage.total_tokens}, requests: {agent_usage.requests}")
    


if __name__ == "__main__":
    asyncio.run(main())
