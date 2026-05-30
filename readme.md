# DB MCP Server + Agent

A Model Context Protocol (MCP) server that connects to SQL databases and an AI agent that uses it.

## What it does

- Connect to SQLite, PostgreSQL, MySQL databases
- Explore schema, tables, columns
- Run SELECT queries safely
- Run write queries (INSERT, UPDATE, DELETE) with user confirmation
- Visualize query results as charts in browser
- Use it in Cursor, VS Code, or via the AI agent

## Folder Structure

```
db-mcp-server/
├── server.py          # main mcp server
├── tools/
│   ├── auth.py        # connect and disconnect
│   ├── read.py        # explore and query
│   ├── write.py       # insert, update, delete with confirmation
│   └── chart.py       # visualize as html chart
├── db/
│   ├── connector.py   # postgres, mysql, sqlite connections
│   └── sessions.py    # in memory session store

agent/
├── agent.py               # ai agent loop
├── tool_definitions.py    # tool definitions for llm
└── .env.example

requirements.txt
```

## Setup

**1. Clone and create virtual environment**
```bash
git clone https://github.com/Charanraju360/db-mcp.git
cd db-mcp
python -m venv .venv

# windows
.venv\Scripts\activate

# mac/linux
source .venv/bin/activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the MCP server**
```bash
# stdio (for cursor/vscode)
python db-mcp-server/server.py --transport stdio

# sse (http clients)
python db-mcp-server/server.py --transport sse

# streamable http
python db-mcp-server/server.py --transport http
```

## Add to Cursor

Create or edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "db-mcp-server": {
      "command": "python",
      "args": ["C:/Users/yourname/db-mcp/db-mcp-server/server.py", "--transport", "stdio"]
    }
  }
}
```

Restart Cursor. You will see the db tools available in agent mode.

## Add to VS Code

Install the MCP extension then add to `settings.json`:

```json
{
  "mcp.servers": {
    "db-mcp-server": {
      "command": "python",
      "args": ["C:/Users/yourname/db-mcp/db-mcp-server/server.py", "--transport", "stdio"]
    }
  }
}
```

## Run the Agent

```bash
cd agent
cp .env.example .env
# add your openrouter api key to .env

python agent.py
```

## Available Tools

| Tool | What it does |
|---|---|
| `tool_connect_db` | connect to db, get token |
| `tool_disconnect_db` | disconnect using token |
| `tool_list_databases` | list all databases |
| `tool_list_tables` | list all tables |
| `tool_describe_table` | show columns and types |
| `tool_get_db_info` | db version and size |
| `tool_execute_query` | run SELECT query |
| `tool_preview_query` | preview write query, get confirmation_id |
| `tool_confirm_execute` | run write query after user approves |
| `tool_cancel_query` | cancel write query |
| `tool_visualize_table` | chart query result in browser |

## How write queries work

```
you: insert a new user
agent: calls preview_query → shows you the query
you: yes
agent: calls confirm_execute → runs it

you: no
agent: calls cancel_query → cancelled
```

## Example Agent Conversation

```
you: connect to my sqlite database at ./test.db
agent: connected. token saved.

you: what tables do i have?
agent: you have 3 tables: users, orders, products

you: show me the schema of users table
agent: users has 4 columns: id (integer), name (text), email (text), created_at (datetime)

you: visualize total orders per user
agent: chart opened in browser
```

## Environment Variables

```
# agent/.env
OPENAI_API_KEY=your_openrouter_key_here
```

## Supported Databases

| Database | db_type value |
|---|---|
| SQLite | `sqlite` |
| PostgreSQL | `postgres` |
| MySQL | `mysql` |
