import json
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.agents import create_react_agent
from langchain.schema import HumanMessage
from configs.config import OPENAI_API_KEY, OPENAI_MODEL


# Placeholder function to simulate external API data
def get_boarding_house(data):
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    return formatted_json


# Placeholder function for casual conversation
def casual_chat(input):
    return f"Just reply this input: {input}"


boarding_house_tool = Tool(
    name="GetBoardingHouse",
    func=get_boarding_house,
    description=("Get the user search specification for boarding house search."),
)


casual_chat_tool = Tool(
    name="CasualConversation",
    func=casual_chat,
    description="Use this tool for casual conversation or general questions that don't involve searching.",
)

# Initialize the LLM (using GPT-3.5 Turbo)
llm = ChatOpenAI(
    model_name=OPENAI_MODEL, temperature=0.5, openai_api_key=OPENAI_API_KEY
)

# Create memory to allow the agent to remember previous interactions
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt_template_string = """
    You are an intelligent assistant capable of two tasks:

    Available tools:
    {tools}

    1. **Boarding House Search:** Use this task to find boarding houses based on criteria provided by the user.
    - Use the 'GetBoardingHouse' tool when the input involves finding a boarding house.
    - Follow these rules when preparing the input:
        a. If the user mentions a low budget but does not specify a price, set 'less_than_price' to 1500000.
        b. If the user mentions a high budget but does not specify a price, set 'greater_than_price' to 2000000.
        c. Adjust the 'greater_than_price' and 'less_than_price' for 'AROUND' filters as follows:
            - Subtract 250000 from 'greater_than_price'.
            - Add 250000 to 'less_than_price'.
        d. Ensure all prices are floating-point numbers and do not include currency symbols.
        e. Null values should be represented as `null`, not as strings.

    2. **Casual Conversation:** Use this task for general chat or any non-search-related input.
    - Use the 'CasualConversation' tool for greetings, questions, or casual remarks.

    ### Required Output Format:
    Your response must follow this format strictly:
    Thought: <Explain your reasoning here> Action: Use one of the following tools: {tool_names}
    Action Input: <JSON-formatted input for the tool>
    
    Current Context:
    Chat History:
    {chat_history}

    User Input:
    {input}

    {agent_scratchpad}
    
    ### Examples:
    User: Saya mencari kos di Ciputat dengan harga sekitar 1.5 juta.
    Thought: The user is looking for a boarding house in Ciputat with a price around 1.5 million. Use the GetBoardingHouse tool. Action: GetBoardingHouse Action Input: {{ "building_title": null, "building_address": "Ciputat", "building_proximity": null, "building_facility": null, "building_note": null, "filter_type": "AROUND", "less_than_price": 1750000, "greater_than_price": 1250000 }}
    User: Apa kabar?
    Thought: The user is engaging in a casual conversation. Use the CasualConversation tool. Action: CasualConversation Action Input: {{"input": "Apa kabar?"}}
    """

react_prompt_template = PromptTemplate(
    input_variables=[
        "input",
        "chat_history",
        "agent_scratchpad",
        "tools",
        "tool_names",
    ],
    template=prompt_template_string,
)

# Create a ReACT agent using the custom prompt template
react_agent = create_react_agent(
    llm=llm,
    tools=[boarding_house_tool, casual_chat_tool],
    prompt=react_prompt_template,
    output_parser=ReActSingleInputOutputParser(),
)

# Initialize the agent executor
agent_executor = AgentExecutor(
    agent=react_agent,
    tools=[boarding_house_tool, casual_chat_tool],
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,  # Enable retry mechanism
    max_steps=3,
)

# Example query for boarding house search
query1 = "deket2 semanggi tuh ada daerah apa aja si?"
response1 = agent_executor.invoke({"input": query1})
print(response1.get("output", "No output returned"))  # Use .get() to avoid KeyError
