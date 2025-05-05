import os
import requests
from dotenv import load_dotenv
from typing import Optional
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

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

def get_DateTime(_=None):
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
# ========================
# NOTION FUNCTIONS
# ========================

def create_task(input_str: str):
    """Create task from input string in format 'title|due_date|status'"""
    parts = input_str.split('|')
    title = parts[0].strip()
    due_date = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    status = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "To Do"
    
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
        return []

    tasks = response.json().get("results", [])
    task_list = []
    for task in tasks:
        props = task["properties"]
        name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else "Untitled"
        status = props["Status"]["select"]["name"] if props["Status"]["select"] else "No Status"
        due_date = props.get("Due Date", {}).get("date", {}).get("start", "No Date")
        task_list.append({"name": name, "status": status, "due_date": due_date})
    
    return task_list

def update_task(task_name: str, new_status: str = None, due_date: str = None):
    """Update task properties including status and due date"""
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
    
    # Build update payload based on provided parameters
    payload = {"properties": {}}
    
    if new_status:
        payload["properties"]["Status"] = {"select": {"name": new_status}}
    
    if due_date:
        payload["properties"]["Due Date"] = {"date": {"start": due_date}}
    
    update_response = requests.patch(patch_url, headers=HEADERS, json=payload)
    return "✅ Task updated!" if update_response.status_code == 200 else f"❌ Failed to update: {update_response.text}"

# ========================
# LANGCHAIN TOOLS
# ========================

tools = [
    Tool(
        name="Create Task",
        func=create_task,
        description="Create a new task in Notion. Input must be in format 'title|due_date|status' (due_date and status optional). Example: 'Finish project|2025-05-10|In Progress'"
    ),
    Tool(
        name="Get Tasks",
        func=lambda _: "\n".join([f"📌 {task['name']} - {task['status']} - {task['due_date']}" for task in get_tasks()]),
        description="Use this to retrieve a list of tasks from Notion."
    ),
    Tool(
        name="Update Task",
        func=update_task,
        description="Update a task in Notion. Input format: 'task_title|new_status|due_date' (new_status and due_date are optional). Example: 'Finish project|Done|2025-05-10'"
    ),
    Tool(
        name="Current Time",
        func=get_DateTime,
        description="Get current datetime in YYYY-MM-DD HH:MM:SS format. Input is ignored."
    )
]

# ========================
# LLM + AGENT SETUP (GROQ)
# ========================

llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    agent_kwargs={
        "prefix": """You are a Notion task assistant. Follow these rules:
1. For task creation: Use format 'title|due_date|status'
2. Status defaults to 'To Do' if not specified
3. Return FINAL ANSWER after operation
"""
    }
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
