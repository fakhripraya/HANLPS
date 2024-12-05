# Source-specific imports
from configs.config import (
    OPENAI_MODEL,
    OPENAI_API_KEY,
    GEMINI_MODEL,
    GEMINI_API_KEY,
)
from src.domain.constants import OPENAI, GEMINI
from src.domain.prompt_templates_v2 import react_prompt_template
from src.infra.langchain_v2.llm.llm import create_open_ai_llm, create_gemini_llm
from src.infra.langchain_v2.tools.tools import tools
from src.interactor.interfaces.logger.logger import LoggerInterface

# Langchain and related libraries
from langchain.agents import create_react_agent


def create_agent(llm_type: str, logger: LoggerInterface) -> None:
    """
    Create a reACT agent
    """
    try:
        client = None
        if llm_type == OPENAI:
            client = create_open_ai_llm(OPENAI_MODEL, OPENAI_API_KEY)
        elif llm_type == GEMINI:
            client = create_gemini_llm(GEMINI_MODEL, GEMINI_API_KEY)
        else:
            raise ValueError("No LLM Found")

        return create_react_agent(
            llm=client,
            tools=tools,
            prompt=react_prompt_template,
        )

    except Exception as e:
        logger.log_exception(f"Error connecting LLM: {e}")
