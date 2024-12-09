import os
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from composio_langchain import ComposioToolSet, Action
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_openai_functions_agent, AgentExecutor

load_dotenv()

llm = AzureChatOpenAI(
    base_url=os.getenv("AOAI_GPT4o_BASE_URL"),
    openai_api_version=os.getenv("AOAI_GPT4o_VERSION"),
    openai_api_key=os.getenv("AOAI_GPT4o_KEY"),
    openai_api_type="azure",
    model=os.getenv("AOAI_GPT4o_MODEL"),
    temperature=0
)

# Initialize the toolset
toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))

prompt = hub.pull("hwchase17/openai-functions-agent")

composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(actions=['GMAIL_SEND_EMAIL'])

task = {
    "recipient": "katariyapranav91@gmail.com",
    "subject": "Reminder: Pending Dues",
    "body": "Dear Pranav,\n\nThis is a reminder regarding your pending dues. Please ensure that the payment is made at your earliest convenience.\n\nBest regards,\Pranav"
}

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute using agent_executor
agent_executor.invoke({"input": task})
