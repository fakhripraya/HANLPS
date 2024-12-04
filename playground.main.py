import time
import json
import os
from dotenv import load_dotenv
from langchain.agents import create_react_agent, Tool, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from src.infra.langchain_v2.memory.memory import LimitedConversationBufferMemory

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(
    model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0.5
)


# Tool 1: Simulate boarding house search
def search_boarding_house(data):
    # Parse the JSON string into a Python dictionary
    jsonobj = json.loads(data)

    # Extract values from the dictionary
    building_address = jsonobj["building_address"]

    if building_address == "Semanggi":
        return f"\n{json.dumps({
        "searched_boarding_houses": [
            {"name": "Cozy Stay", "location": "Semanggi", "price": 1500000},
            {"name": "Kostey Kost", "location": "Bendungan hilir", "price": 1000000},
        ]
    }, indent=4)}\n"
    else:
        return f"\n{json.dumps({
            "searched_boarding_houses": []
        }, indent=4)}\n"


# Tool 3: Simulate boarding house search
def save_location(data):
    return f"\n Is location successfully saved: {True}\n"


# Define the tools
tools = [
    Tool(
        name="SearchBoardingHouse",
        func=search_boarding_house,
        description="""
        Search for boarding houses based on the specified criteria.

        ### Input Fields (JSON format):
        - building_title: Title of the building.
        - building_address: Building's address or area.
        - building_proximity: Nearby landmarks, separated by commas.
        - building_facility: List of facilities, separated by commas.
        - building_note: Important notes or rules.
        - filter_type: Filter type ("LESS_THAN", "GREATER_THAN", or "AROUND").
        - less_than_price: Maximum price (required for "LESS_THAN" or "AROUND" filters).
        - greater_than_price: Minimum price (required for "GREATER_THAN" or "AROUND" filters).
        - is_next: Set to true if continuing a previous search.

        ### Rules:
        - Default values are null; if an input field is not provided, set it to null.
        - Prices must be positive; values <= 0 default to 0.
        - For "AROUND" filters, adjust prices by ±250,000 units.
        - Reset previous filters if a new building title is provided.
        - Ensure numeric values are floats, not strings.
        - No currency symbols in price values.

        ### Output:
        Return the results in JSON format without additional actions.
        """,
    ),
    Tool(
        name="SaveLocation",
        func=save_location,
        description="""
        Save the location to the database

        ### Input Fields (JSON format):
        - building_title: Title of the building.
        - building_address: Building's address or area.
        - building_proximity: Nearby landmarks, separated by commas.
        - building_facility: List of facilities, separated by commas.
        - building_note: Important notes or rules.
        - filter_type: Filter type ("LESS_THAN", "GREATER_THAN", or "AROUND").
        - less_than_price: Maximum price (required for "LESS_THAN" or "AROUND" filters).
        - greater_than_price: Minimum price (required for "GREATER_THAN" or "AROUND" filters).
        - is_next: Set to true if continuing a previous search.

        ### Rules:
        - Default values are null; if an input field is not provided, set it to null.
        - Prices must be positive; values <= 0 default to 0.
        - For "AROUND" filters, adjust prices by ±250,000 units.
        - Reset previous filters if a new building title is provided.
        - Ensure numeric values are floats, not strings.
        - No currency symbols in price values.

        ### Condition
        - If return True, the location is successfully saved
        
        ### Output:
        - If the action is successful, return a confirmation message in string format.
        - If unsuccessful, provide an error message explaining the issue.
        """,
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
    You are Pintrail, a multi-tasking assistant who spoke mainly in Bahasa Indonesia language but can also understand and speak different language
    You are capable of performing Task with tools:

    ### Available Tools:
    {tool_names}

    ### All Tools Details
    {tools}

    You are capable of performing two main task with those tools:
    1. **Boarding House Search:** Use the 'SearchBoardingHouse' tool when the user asks for boarding house information.
    2. **Save Location:** Use the 'SaveLocation' tool when the user ask to save the boarding house.

    You also capable of performing two main chat completions task:
    1. **Object Comparison:** when the user asks for specific boarding house objects comparison, explain the comparison between those objects.
    2. **Casual Conversation:** reply casually if the user input is a casual chat.
    
    ### Important Guidelines:
    - Carefully analyze the user's input to determine the most appropriate tool to use, or decide if a simple chat completion is sufficient to address the request.
    - Structure your response strictly in the following format:
    Thought: <Mandatory. Explain your reasoning>
    Action: <Mandatory. Your action>
    Action Input: <Mandatory. This is your input, could be JSON-formatted input>

    ### Required Output Format:
    Your response must follow this format strictly:
    Thought: <Mandatory. Explain your reasoning here>
    Final Answer: <Mandatory. Pure alphabet only String or JSON-formatted output>

    ### Rules:
    - Do not include a final answer if an action is being performed. Follow strictly: Thought, Action, Action Input.
    - After successfully obtaining valid information from a tool, respond directly to the user without calling another tool.
    - If the task is complete, avoid unnecessary actions.
    - Respond the conversations using the slang language of Indonesian Jaksel Gen Z.
    - Be a cool Jaksel Gen Z friend who is fun to talk to and very helpful.

    ### Context:
    Chat History: {chat_history}
    User Input: {input}
    {agent_scratchpad}
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
    max_execution_time=10,
    max_iterations=10,
    memory=memory,
    allow_dangerous_code=True,
    handle_parsing_errors=True,
)

# Record start time
start_time = time.time()

query = "kosan semanggi harga 1.5 dong"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

query = "ada lagi gak?"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

query = "di lebak bulus ada ga?"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

query = "yaudah simpenin yang di semanggi ya"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

# Record end time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Processing time: {elapsed_time} seconds")
