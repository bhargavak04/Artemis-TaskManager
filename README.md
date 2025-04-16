
# Artemis AI Agent 🤖

A conversational AI agent integrated with Notion for task management, powered by Groq's fast LLMs (Llama 3/Mixtral) via LangChain.

## Features ✨

- **Task Management**:
  - Create tasks in Notion
  - View all tasks with status
  - Update task status
- **AI Assistant**:
  - Natural language understanding
  - Context-aware responses
  - Powered by Groq's ultra-fast LLMs

## Tech Stack 🛠️

- **Backend**: Python
- **AI Framework**: LangChain
- **LLM Provider**: Groq (Llama 3 8B/Mixtral 8x7B)
- **Database**: Notion (as a backend)
- **Environment**: Python virtual environment

## Prerequisites 📋

- Python 3.8+
- Notion account with a database setup
- Groq API key (free tier available)

## Setup Instructions 🚀

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bhargavak04/Artemis-TaskManager.git
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv envs
   source envs/bin/activate  # On Windows: envs\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the backend directory with:
   ```env
   NOTION_API_KEY=your_notion_integration_key
   NOTION_DATABASE_ID=your_database_id
   GROQ_API_KEY=your_groq_api_key
   ```

5. **Configure Notion Database**:
   - Create a database in Notion with these properties:
     - Name (Title)
     - Status (Select: "To Do", "In Progress", "Done")
     - Due Date (Date) - optional

6. **Run the application**:
   ```bash
   python main.py
   ```

## Usage Examples 💬

```
🤖 Artemis AI Agent Ready!

🗣️ You: Add "Complete project documentation" to my tasks
🤖 Artemis: ✅ Task created!

🗣️ You: Show me all tasks
🤖 Artemis: 📌 Complete project documentation - To Do - Due: No Date
📌 Buy groceries - Done - Due: 2024-05-20

🗣️ You: Mark "Complete project documentation" as done
🤖 Artemis: ✅ Task updated!
```

## Project Structure 📂

```
backend/
├── main.py            # Main application logic
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Troubleshooting 🛠

**Error: Client.__init__() got an unexpected keyword argument 'proxies'**
- Solution: Upgrade Groq package:
  ```bash
   pip install --upgrade groq langchain-groq
   ```

**Notion API Issues**:
- Verify your database has the correct properties
- Check your integration has access to the database

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request.

## License 📄

This project is licensed under the MIT License.
```



