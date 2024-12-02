import time
import json
import os
from dotenv import load_dotenv
from langchain.agents import create_react_agent, Tool, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate


# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0.5)

# Tool 1: Simulate boarding house search
def search_boarding_house(data):
    print(data)
    return f"\n{json.dumps({
        "results": [
            {"name": "Cozy Stay", "location": "Semanggi", "price": 1500000},
            {"name": "Kostey Kost", "location": "Bendungan hilir", "price": 1000000},
        ],
        "output_message": "<Agent message explaining the results>",
    }, indent=4)}\n"

# Tool 2: Simulate boarding house search
def compare_object(data):
    print(data)
    return f"\n{json.dumps({
        "objects": [
            {"name": "Cozy Stay", "location": "Semanggi, 2 KM dari senayan", "price": 1500000},
            {"name": "Kostey Kost", "location": "Bendungan hilir, 4 KM dari senayan", "price": 1000000},
        ],
        "output_message": "<Agent message comparing the objects>",
    }, indent=4)}\n"

# Tool 3: Simulate boarding house search
def save_location(data):
    return f"\n{json.dumps({
        "is_success": True,
        "output_message": "<Agent message explaining that location has been saved>",
    }, indent=4)}\n"

# Define the tools
tools = [
    Tool(
        name="SearchBoardingHouse",
        func=search_boarding_house,
        description="""
        Search for boarding houses based on the search specification input.
        
        ### Important for SearchBoardingHouse input
        This is the specification input, only provide the following fields in a JSON dict, where applicable:
        building_title: This is the title of the building
        building_address: This is the address or the area of where the building in
        building_proximity: This is the proximity around the building or the building area
        building_facility: This is the list of facility that the building has
        building_note: This is some random note that need to be put in mind, this can be rules, or anything to be noted
        filter_type: This is the filter type in enums [LESS_THAN, GREATER_THAN, AROUND] that is based on the chat context
        less_than_price: This is the price value that follows the "filter_type" property value, the value is determined if the "filter_type" is either "LESS_THAN" or "AROUND"
        greater_than_price: This is the price value that follows the "filter_type" property value, the value is determined if the "filter_type" is either "GREATER_THAN" or "AROUND"
        is_next: If the user demand to continue the search with the same search specification

        ### Rules specific for SearchBoardingHouse input
        - Default value is null
        - Filter price can't be less than or equal 0 if the filter reach 0 or minus, give 0 value
        - For filter type AROUND and is not a price range, make sure to adjust the price for greater_than_price: xxx subtracted by 250000 and less_than_price: xxx added by 250000
        - Nullify previous asked filter price if building title provided
        - Null value are not string 
        - Numbers are float not string
        - The price number are in floating number type as we won't accept any currency symbol
        """
    ),
    Tool(
        name="ObjectComparison",
        func=compare_object,
        description="""
        Compare the given objects, can be more than 2 objects
        
        ### Input object specification
        Only provide the following fields in a JSON dict, where applicable:
        building_address: This is the address or the area of where the building in
        building_proximity: This is the proximity around the building or the building area
        building_facility: This is the list of facility that the building has
        building_note: This is some random note that need to be put in mind, this can be rules, or anything to be noted
        building_price: This is the building rent price
        building_geolocation: This is the building geolocation coordinate

        ### Rules specific for ObjectComparison input
        - Default value is null
        - Null value are not string 
        - Numbers are float not string
        - The price number are in floating number type as we won't accept any currency symbol
        """
    ),
    Tool(
        name="SaveLocation",
        func=save_location,
        description="Save the location to the database"
    ),
]

# Advanced ReAct prompt template
react_prompt_template = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad", "tools", "tool_names"],
    template="""
    You are Pintrail, a multi-tasking assistant who spoke mainly in Bahasa Indonesia language but can also understand and speak different language
    You are capable of performing four main tasks:

    1. **Boarding House Search:** Use the 'SearchBoardingHouse' tool when the user asks for boarding house information.
    2. **Object Comparison:** Use the 'ObjectComparison' tool when the user asks for specific boarding house object comparison.
    3. **Save Location:** Use the 'SaveLocation' tool when the user ask to save the boarding house.
    4. **Casual Conversation:** reply casually if the user input is a casual chat.
    
    ### Important Guidelines for all tools:
    - Always analyze the user input thoroughly to decide which tool to use.
    - Structure your response strictly in the following format:
    Thought: <Explain your reasoning>
    Action: <Select the tool>
    Action Input: <JSON-formatted input>

    ### Required Output Format:
    Your response must follow this format strictly:
    Thought: <Explain your reasoning here>
    Final Answer: <JSON-formatted output>

    ### Rules:
    - Do not include a final answer if an action is being performed. Follow strictly: Thought, Action, Action Input.
    - After successfully obtaining valid information from a tool, respond directly to the user without calling another tool.
    - If the task is complete, return the results in a readable format and avoid unnecessary actions.
    - Respond the conversations using the slang language of Indonesian Jaksel Gen Z.
    - Be a cool Jaksel Gen Z friend who is fun to talk to and very helpful.

    ### Context:
    Chat History: {chat_history}
    User Input: {input}
    {agent_scratchpad}

    Available Tools:
    {tools}

    Available Tool Names:
    {tool_names}
    """
)

# Create the ReAct agent
react_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt_template,
)

# Initialize the agent executor
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent_executor = AgentExecutor(
    agent=react_agent,
    tools=tools,
    verbose=True,
    max_execution_time=10,
    max_iterations=10,
    memory=memory,
    allow_dangerous_code=True,
    handle_parsing_errors=True
)

# Record start time
start_time = time.time()

query = "kosan semanggi harga 1.5 dong"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

query = "ada lagi gak?"
response = agent_executor.invoke({"input": query})
print(response.get("output", "No output returned"))

# Record end time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Processing time: {elapsed_time} seconds")