# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import time
import json
from configs.config import OPENAI_API_KEY, OPENAI_MODEL

from src.domain.enum.tool_types.tool_types import ToolType
from src.domain.pydantic_models.agent_tool_output.agent_tool_output import AgentToolOutput
from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory

from langchain.agents import create_react_agent, Tool, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_community.utilities import SearxSearchWrapper

# Initialize the LLM
llm = ChatOpenAI(
    model_name=OPENAI_MODEL,
    openai_api_key=OPENAI_API_KEY,
    temperature=0.3,  # Lower values reduce randomness, enhancing logical responses
    top_p=0.85,  # Controls nucleus sampling; focuses on most probable tokens
    frequency_penalty=0.2,  # Reduces repetition in responses
    presence_penalty=0.1,  # Encourages more contextually relevant output
)


# Tool 1: Simulate nearby poi search
def search_poi_by_address(input):
    # Parse the JSON string into a Python dictionary
    result = str(input).strip("`").strip("json").strip("`").strip()
    data = json.loads(result)
    print(data)

    return f"\n{json.dumps({
        "input_code": ToolType.SEARCH_POINT_OF_INTEREST.value,
        "input_field": data
    }, indent=4)}\n"

# Tool 2: Simulate specific building search
def search_specific_by_address(input):
    # Parse the JSON string into a Python dictionary
    result = str(input).strip("`").strip("json").strip("`").strip()
    data = json.loads(result)
    print(data)

    return f"\n{json.dumps({
        "input_code": ToolType.SEARCH_SPECIFIC_LOCATION.value,
        "input_field": data
    }, indent=4)}\n"

# Tool 3: Simulate save location
def save_location(input):
    result = str(input).strip("`").strip("json").strip("`").strip()
    data = json.loads(result)
    print(data)

    return f"\n{json.dumps({
        "input_code": ToolType.SAVE_LOCATION.value,
        "input_field": data
    }, indent=4)}\n"

# Tool 4: Simulate directional navigation helper
def get_direction(input):
    result = str(input).strip("`").strip("json").strip("`").strip()
    data = json.loads(result)
    print(data)

    return f"\n{json.dumps({
        "input_code": ToolType.GET_DIRECTION.value,
        "input_field": data
    }, indent=4)}\n"


# Define the tools
tools = [
    Tool(
        name="SearchPointOfInterest",
        func=search_poi_by_address,
        description="Search for nearby point of interest based on the specified address.",
    ),
    Tool(
        name="SearchSpecificLocation",
        func=search_specific_by_address,
        description="Search for specific given address location.",
    ),
    Tool(
        name="SaveLocation",
        func=save_location,
        description="Save the location data temporarily.",
    ),
    Tool(
        name="GetDirection",
        func=get_direction,
        description="Get the directional navigation start to end geocode data.",
    ),
]

# Advanced ReAct prompt template
react_prompt_template = PromptTemplate(
    input_variables=[
        "input",
        "chat_history",
        "agent_scratchpad",
        "tools",
        "tool_names",
    ],
    template="""
    You are Pintrail, a multi-tasking assistant mainly for maps, direction, and specific building search

    You have access to the following tools:
    {tools}
    
    Tools explanation:
    1. Nearby POI Search: Use the 'SearchPointOfInterest' tool when the user asks for information nearby given address, either its a boarding house, hotel, or residence.
    2. Specific Location Search: Use the 'SearchSpecificLocation' tool when the user asks for information of specific given address location.
    3. Save Location: Use the 'SaveLocation' tool when the user ask to save the building data.
    4. Get Directional Navigation: Use the 'GetDirection' tool when the user ask for directional navigation.
    
    Tools Input Guidelines:
        Input Fields (JSON format):
        - building_title: Title of the building.
        - building_address: Building's address or area.
        - building_proximity: Nearby landmarks, separated by commas.
        - building_facility: List of facilities, separated by commas.
        - building_note: Important notes or rules.
        - filter_type: Filter type ("LESS_THAN", "GREATER_THAN", or "AROUND").
        - less_than_price: Maximum price (required for "LESS_THAN" or "AROUND" filters).
        - greater_than_price: Minimum price (required for "GREATER_THAN" or "AROUND" filters).
        - is_currently_ask_for_homestay: Set to true if the user is asking for homestay in this current prompt
        - is_next: Set to true if the user is asking for more option or continuing the search.

        Input Field Rules:
        - Default values are null; if an input field is not provided, set the value to null.
        - Prices must be positive; values <= 0 default to 0.
        - For "AROUND" filters, adjust prices by ±250,000 units.
        - Reset previous filters if a new building title is provided.
        - Ensure numeric values are floats, not strings.
        - No currency symbols in price values.
        
        This is the valid output in JSON Formatted output, stop when you receieve this value:
        1. {{"input_code": "SEARCH_POINT_OF_INTEREST", "input_field": <Tool input field value>}}     
        2. {{"input_code": "SEARCH_SPECIFIC_LOCATION", "input_field": <Tool input field value>}}
        3. {{"input_code": "SAVE_LOCATION", "input_field": <Tool input field value>}}
        4. {{"input_code": "GET_DIRECTION", "input_field": <Tool input field value>}}

    You also capable of performing two main chat completions task:
    1. Object Comparison: when the user asks for specific building objects comparison, explain the comparison between those objects.
    2. Casual Conversation: reply casually if the user input is a casual chat.
    
    Important Guidelines:
    - Carefully analyze the user's input to determine the most appropriate tool to use, or decide if a simple chat completion is sufficient to address the request.
    - Structure your response strictly in the following format:
        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        (this Thought/Action/Action Input/Observation can repeat 3 times)

    Required Output Format For Tools:
    Your response MUST follow this format strictly:
        Thought: Do I need to use a tool? No
        Final Answer: <your response here, only response in the required structured JSON format>

    Required Output Format For Chat Completions:
    Your response MUST follow this format strictly:
        Thought: Do I need to use a tool? No
        Final Answer: <your response here>

    Rules:
    - Do not include a final answer if an action is being performed. Follow strictly: Thought, Action, Action Input.
    - If the task is complete, avoid unnecessary actions.
    - If you use tools, don't give the output in string. only give the output in structured JSON format

    Context:
    Chat History: {chat_history}

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
    """,
)

# Create the ReAct agent
react_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt_template,
)

# Create the memory instance
memory = LimitedConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    k=10,  # Store only the last 10 messages
)

# Initialize the agent executor
agent_executor = AgentExecutor(
    agent=react_agent,
    tools=tools,
    verbose=True,
    max_execution_time=60,
    max_iterations=15,
    memory=memory,
    allow_dangerous_code=True,
    handle_parsing_errors=True,
)

# Record start time
start_time = time.time()

# search po query
query = "info kost blok m harga 2.5 jtan dong"
response = agent_executor.invoke({"input": query}).get("output", "No output returned")

json_data = json.loads(response)

agent_output = AgentToolOutput(**json_data)
print(agent_output)

# search specific building query
query = "eh kalo mall blok m dimana ya"
response = agent_executor.invoke({"input": query}).get("output", "No output returned")

json_data = json.loads(response)

agent_output = AgentToolOutput(**json_data)
print(agent_output)

# save location
query = "simpenin ya yang blok m"
response = agent_executor.invoke({"input": query}).get("output", "No output returned")
print(response)

json_data = json.loads(response)

agent_output = AgentToolOutput(**json_data)
print(agent_output)

# get direction
query = "oh iya tunjukin jalannya dong"
response = agent_executor.invoke({"input": query}).get("output", "No output returned")

print(response)
json_data = json.loads(response)

agent_output = AgentToolOutput(**json_data)
print(agent_output)

# default response
query = "mahal"
response = agent_executor.invoke({"input": query}).get("output", "No output returned")
print(agent_executor.memory.load_memory_variables({}).get('chat_history', []))
for message in agent_executor.memory.load_memory_variables({}).get('chat_history', []):
    if isinstance(message, HumanMessage):
        print(f"Human: {message.content}")
    elif isinstance(message, AIMessage):
        print(f"AI: {message.content}")
    else:
        print("Unknown message format:", message)

# s = SearxSearchWrapper(searx_host="https://searx.be/")
# s.run("what is a large language model?")

# Record end time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Processing time: {elapsed_time} seconds")
