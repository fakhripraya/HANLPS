from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def create_open_ai_llm(llm_model, key) -> ChatOpenAI:
    """
    Create OpenAI LLM and register it as dependency
    """
    client = ChatOpenAI(model=llm_model, api_key=key, temperature=0.5)
    return client


def create_gemini_llm(llm_model, key) -> ChatGoogleGenerativeAI:
    """
    Create Gemini LLM and register it as dependency
    """
    baseUrl = "https://generativelanguage.googleapis.com"
    version = "v1beta"
    client = ChatGoogleGenerativeAI(
        model=llm_model,
        google_api_key=key,
        temperature=0.5,
        baseUrl=baseUrl,
        max_retries=3,
        version=version,
    )
    return client
