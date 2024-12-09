import os
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from composio_langchain import ComposioToolSet, Action

load_dotenv()

llm = AzureChatOpenAI(
    base_url=os.getenv("AOAI_GPT4o_BASE_URL"),
    openai_api_version=os.getenv("AOAI_GPT4o_VERSION"),
    openai_api_key=os.getenv("AOAI_GPT4o_KEY"),
    openai_api_type="azure",
    model=os.getenv("AOAI_GPT4o_MODEL"),
    temperature=0
)

prompt = hub.pull("hwchase17/openai-functions-agent")   


# Get All the tools

composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(actions=['GOOGLEMEET_CREATE_MEET'])

task = "Create a google meet link."

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute using agent_executor
agent_executor.invoke({"input": task})