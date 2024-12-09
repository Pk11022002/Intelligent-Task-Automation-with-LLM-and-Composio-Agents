import os

from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = AzureChatOpenAI(
    base_url=os.getenv("AOAI_GPT4o_BASE_URL"),
    openai_api_version=os.getenv("AOAI_GPT4o_VERSION"),
    openai_api_key=os.getenv("AOAI_GPT4o_KEY"),
    openai_api_type="azure",
    model=os.getenv("AOAI_GPT4o_MODEL"),
    temperature=0
)

# prompt = hub.pull("hwchase17/openai-functions-agent")

# tool_set = ComposioToolSet(entity_id="Jessica")
# tools = tool_set.get_tools(actions=[Action.GOOGLECALENDAR_CREATE_EVENT])

# # functions = [convert_to_openai_function(t) for t in tools]

# agent = create_openai_functions_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# task = """Start time of the event: October 18, 2024, 2:00 PM IST
#         Duration of the event: 1 hours
#         Location of the event: Mumbai
#         Description of the event: Team meeting 
#         List of attendees' email addresses:
#         pranav@scogo.in
#         katariyapranav91@gmail.com
#         Specific settings for the event:
#         Guests can modify the event: Yes
#         Enable Google Meet video conferencing: Yes      
# """

# # Create a Google Meet link: https://meet.google.com/qim-wbfk-vzu

# # Execute using agent_executor
# while True:
#     user_input = input("Query:")   

#     if user_input.lower() == "bye" :
#       break  

#     execute_agent = agent_executor.invoke({"input": user_input})

#     print(execute_agent['output'])


from composio_langchain import ComposioToolSet, Action
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
import datetime
from langchain_core.messages import AIMessage, HumanMessage


os.environ['COMPOSIO_API_KEY'] = "7juf0lbeoq6yq54vysc6l"

tool_set = ComposioToolSet(entity_id="Jessica")
tools = tool_set.get_tools(actions=[Action.GOOGLECALENDAR_CREATE_EVENT])

history = []

prompt_template = """
    You are an agent specifically designed for scheduling online meets.
    Your only task is to schedule online google meets of 30 minutes.
    You should ask date and time to the user keeping in mind the current date is {current_datetime} IST.
    Schedule the meets according to IST timezone only.
    You should ask the reciever's email ID which should be used in attendees.

    {agent_scratchpad}

    User input: {input}
    Conversation history: {history}

    Once a meet is created reply with "have a good meet"
"""

PROMPT = PromptTemplate(
                template=prompt_template, input_variables=[
                    'agent_scratchpad', 'current_datetime', 'input', 'history']
            )

# functions = [convert_to_openai_function(t) for t in tools]
agent = create_openai_tools_agent(llm, tools, PROMPT)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while True:
    query = input("Query: ")

    if query.lower() == 'bye' or query.lower() == 'q':
        break

    r = agent_executor.invoke({"input": query, "current_datetime": datetime.datetime.now(), "history": history})
    history.append(HumanMessage(content=query))
    history.append(AIMessage(content=r['output']))

    if "Have a good meet!" in r['output']:
        break

    print(f"AGENT: {r['output']}")
    


