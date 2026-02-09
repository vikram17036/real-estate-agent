# Standard library imports
import asyncio
import os

# Third-party library imports
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Optional imports
try:
    import logfire
    logfire.configure(send_to_logfire='if-token-present')
except ImportError:
    logfire = None

# Local application imports
try:
    from src.agent.realtor_agent_langgraph import get_restaurant_agent
    from src.agent.agent_config import AgentDependencies
    from src.models.agent_schedule_config import AgentScheduleConfig
except ModuleNotFoundError:
    from agent.realtor_agent_langgraph import get_restaurant_agent
    from agent.agent_config import AgentDependencies
    from models.agent_schedule_config import AgentScheduleConfig

# Optional cost tracking - Note: Cost tracking will need to be adapted for LangGraph
# try:
#     from agent.agent_cost import compute_cost
#     COST_TRACKING_AVAILABLE = True
# except ImportError:
COST_TRACKING_AVAILABLE = False

async def main():
    make_webhook_url = os.getenv("MAKE_WEBHOOK_URL")
    agent_timezone = os.getenv("AGENT_TIMEZONE", "America/New_York")
    agent_schedule_config = AgentScheduleConfig(
        timezone=agent_timezone
    ) 

    # Initialize agent dependencies
    agent_deps = AgentDependencies(
        make_webhook_url=make_webhook_url,
        agent_schedule_config=agent_schedule_config
    )

    # Create LangGraph agent
    agent = get_restaurant_agent(agent_deps)

    print("Welcome to the Restaurant Reservation Agent Chat!")
    message = "Hello"

    # Initialize state with messages
    config = {}
    state = {
        "messages": []
        # Note: selected_time_slot will be added automatically when needed
    }

    # Chat loop
    while True:

        if message.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Add user message to state
        state["messages"].append(HumanMessage(content=message))
        
        # Invoke the agent
        result = await agent.ainvoke(state, config)
        
        # Update state
        state = result
        
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
        
        print(f"Agent: {agent_response}")

        # Prompt next input
        message = input("You: ")

    # Note: Cost tracking would need to be adapted for LangGraph
    if COST_TRACKING_AVAILABLE:
        print("Cost tracking not yet implemented for LangGraph version")
    
    


if __name__ == "__main__":
    asyncio.run(main())
