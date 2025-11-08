# Standard library imports
import os

# Third-party library imports
from dotenv import load_dotenv

# Pydantic AI imports
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Local application imports
try:
    from src.agent.agent_config import SYSTEM_PROMPT, AgentDependencies
except ModuleNotFoundError:
    from agent.agent_config import SYSTEM_PROMPT, AgentDependencies

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_KEY")
llm_model = os.getenv("OPEN_ROUTER_LLM_MODEL")

# model = OpenAIModel(
#     llm_model,
#     provider=OpenAIProvider(
#         base_url='https://openrouter.ai/api/v1',
#         api_key=openrouter_api_key
#     )
# )

# Overriding to use OpenAI directly
model = os.getenv("OPENAI_LLM_MODEL")
openai_key = os.getenv("OPENAI_API_KEY")


realtor_agent = Agent(
    model = model,
    system_prompt = SYSTEM_PROMPT,
    temperature=0.3,
    deps_type=AgentDependencies,
    output_type=str,
    instrument=True
)

# Force import of tools so decorators run
try:
    from src.agent.tools import recommend_properties  # noqa: F401
    from src.agent.tools import get_agent_availability  # noqa: F401
    from src.agent.tools import schedule_appointment  # noqa: F401
except ModuleNotFoundError:
    from agent.tools import recommend_properties  # noqa: F401
    from agent.tools import get_agent_availability  # noqa: F401
    from agent.tools import schedule_appointment  # noqa: F401