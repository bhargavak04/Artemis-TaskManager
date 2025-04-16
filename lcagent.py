import os
import requests
from dotenv import load_dotenv
from typing import Optional
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq

# Load .env file
load_dotenv()

# Environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ========================
# NOTION FUNCTIONS
# ========================

def create_task(title: str, due_date: Optional[str] = None, status: str = "To Do"):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": status}},
        }
    }
    if due_date:
        payload["properties"]["Due Date"] = {"date": {"start": due_date}}

    response = requests.post(url, headers=HEADERS, json=payload)
    return "✅ Task created!" if response.status_code == 200 else f"❌ Failed: {response.text}"

def get_tasks():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        return f"❌ Failed: {response.text}"

    tasks = response.json().get("results", [])
    output = []
    for task in tasks:
        props = task["properties"]
        name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else "Untitled"
        status = props["Status"]["select"]["name"] if props["Status"]["select"] else "Unknown"
        due_date = props.get("Due Date", {}).get("date", {}).get("start", "No Date")
        output.append(f"📌 {name} - {status} - Due: {due_date}")
    return "\n".join(output)

def update_task(task_name: str, new_status: str = "Done"):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    query = {
        "filter": {
            "property": "Name",
            "title": {
                "contains": task_name
            }
        }
    }
    response = requests.post(url, headers=HEADERS, json=query)
    tasks = response.json().get("results", [])

    if not tasks:
        return f"❌ No task found with name containing '{task_name}'"

    task_id = tasks[0]["id"]

    patch_url = f"https://api.notion.com/v1/pages/{task_id}"
    payload = {
        "properties": {
            "Status": {"select": {"name": new_status}}
        }
    }
    update_response = requests.patch(patch_url, headers=HEADERS, json=payload)
    return "✅ Task updated!" if update_response.status_code == 200 else f"❌ Failed to update: {update_response.text}"

# ========================
# LANGCHAIN TOOLS
# ========================

tools = [
    Tool(
        name="Create Task",
        func=lambda text: create_task(text),
        description="Use this to add a task to the Notion Student Planner. Input should be the task title. Optional: include due date."
    ),
    Tool(
        name="Get Tasks",
        func=lambda _: get_tasks(),
        description="Use this to retrieve a list of tasks from Notion."
    ),
    Tool(
        name="Update Task",
        func=lambda text: update_task(text),
        description="Use this to update a task status to Done. Input should be the task title."
    )
]

# ========================
# LLM + AGENT SETUP (GROQ)
# ========================

llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",  # or try "mixtral-8x7b-32768"
    groq_api_key=os.getenv("GROQ_API_KEY")
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ========================
# MAIN TEST
# ========================

if __name__ == "__main__":
    print("🤖 Artemis AI Agent Ready!\n")

    while True:
        user_input = input("🗣️ You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        print("🤖 Artemis:", agent.run(user_input))
