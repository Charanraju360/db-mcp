# this file defines all the tools the agent can use
# these tools call the mcp server tools internally
# we define them in openai tool format so the llm knows what to call

tools = [
    {
        "type": "function",
        "function": {
            "name": "tool_connect_db",
            "description": "connect to a database. db_type can be sqlite, postgres or mysql. returns a token to use in other tools",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_type": {"type": "string", "description": "sqlite, postgres or mysql"},
                    "host": {"type": "string", "description": "database host. use empty string for sqlite"},
                    "port": {"type": "integer", "description": "database port. use 0 for sqlite"},
                    "user": {"type": "string", "description": "database user. use empty string for sqlite"},
                    "password": {"type": "string", "description": "database password. use empty string for sqlite"},
                    "database": {"type": "string", "description": "database name or sqlite file path"}
                },
                "required": ["db_type", "host", "port", "user", "password", "database"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_disconnect_db",
            "description": "disconnect from database using the token",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "token from connect_db"}
                },
                "required": ["token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_list_databases",
            "description": "list all databases on the connected server",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"}
                },
                "required": ["token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_list_tables",
            "description": "list all tables in the current database",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"}
                },
                "required": ["token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_describe_table",
            "description": "show columns, types and constraints of a table",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "table_name": {"type": "string"}
                },
                "required": ["token", "table_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_db_info",
            "description": "get basic info about the database like version and size",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"}
                },
                "required": ["token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_execute_query",
            "description": "run a SELECT query and get results",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "query": {"type": "string", "description": "SELECT query to run"}
                },
                "required": ["token", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_preview_query",
            "description": "preview a write query before running. returns confirmation_id. always call this before execute",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "query": {"type": "string", "description": "INSERT, UPDATE, DELETE query"}
                },
                "required": ["token", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_confirm_execute",
            "description": "user approved the query. run it using confirmation_id",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirmation_id": {"type": "string"}
                },
                "required": ["confirmation_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_cancel_query",
            "description": "user rejected the query. cancel it using confirmation_id",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirmation_id": {"type": "string"}
                },
                "required": ["confirmation_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_visualize_table",
            "description": "run a SELECT query and show result as a chart in browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "query": {"type": "string"},
                    "title": {"type": "string", "description": "chart title"}
                },
                "required": ["token", "query"]
            }
        }
    }
]