import os
import re
from datetime import datetime
from dotenv import load_dotenv
from composio_langchain import Action, ComposioToolSet
from langchain import hub
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from composio.client.collections import TriggerEventData

load_dotenv()

os.environ['COMPOSIO_API_KEY'] = ""

llm = AzureChatOpenAI(
    base_url=os.getenv("AOAI_GPT4o_BASE_URL"),
    openai_api_version=os.getenv("AOAI_GPT4o_VERSION"),
    openai_api_key=os.getenv("AOAI_GPT4o_KEY"),
    openai_api_type="azure",
    model=os.getenv("AOAI_GPT4o_MODEL"),
    temperature=0
)

composio_toolset = ComposioToolSet() 

schedule_tool = composio_toolset.get_tools(
    actions=[
        Action.GOOGLECALENDAR_FIND_FREE_SLOTS,
        Action.GOOGLECALENDAR_CREATE_EVENT,
        Action.GMAIL_CREATE_EMAIL_DRAFT,
    ]
)

email_tool = composio_toolset.get_tools(actions=[Action.GMAIL_CREATE_EMAIL_DRAFT])
date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timezone = datetime.now().astimezone().tzinfo

prompt = hub.pull("hwchase17/openai-functions-agent")
query_agent = create_openai_functions_agent(llm, schedule_tool, prompt)
agent_executor = AgentExecutor(agent=query_agent, tools=schedule_tool, verbose=True)

def extract_sender_email(payload):
    delivered_to_header_found = False
    for header in payload["headers"]:
        if header.get("name", "") == "Delivered-To" and header.get("value", "") != "":
            delivered_to_header_found = True
    print("delivered_to_header_found: ", delivered_to_header_found)
    if not delivered_to_header_found:
        return None 
    for header in payload["headers"]:
        if header["name"] == "From":
            # Regular expression to extract email from the 'From' header value
            match = re.search(r"[\w\.-]+@[\w\.-]+", header["value"])
            if match:
                return match.group(0)
    return None


listener = composio_toolset.create_trigger_listener()

@listener.callback(filters={"trigger_name": "GMAIL_NEW_GMAIL_MESSAGE"})
def callback_new_message(event: TriggerEventData) -> None:
    print("here in the function")
    payload = event.payload

    if not payload:
        print("Error: Payload is empty.")
        return

    print(payload)

    thread_id = payload.get('threadId')
    message = payload.get('messageText')
    sender_mail = payload.get('sender')
    if sender_mail is None:
        print("No sender email found")
        return
    print(f"Sender email: {sender_mail}")

    query_task = f"""
            1. Analyze the email content and decide if an event should be created. 
                a. The email was received from {sender_mail} 
                b. The content of the email is: {message} 
                c. The thread id is: {thread_id}. 
            2. If you decide to create an event, try to find a free slot 
            using Google Calendar Find Free Slots action.
            3. Once you find a free slot, use Google Calendar Create Event 
            action to create the event at a free slot and send the invite to {sender_mail}.
            If an event was created, draft a confirmation email for the created event. 
            The receiver of the mail is: {sender_mail}, the subject should be meeting scheduled and body
            should describe what the meeting is about
            """
    
    # Execute the agent
    try:
        res = agent_executor.invoke({"input": query_task})
        print("Agent response:", res)
        
        # Check if the response indicates success
        if isinstance(res, str) and "event created" in res.lower():  # Ensure res is a string
            print("Calendar event successfully created.")
        else:
            print("No event created. Response:", res)
    except Exception as e:
        print("Error executing agent:", str(e))


print("Subscription created!")
listener.listen()




