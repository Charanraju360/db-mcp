import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from tool_definitions import tools

# add parent folder to path so we can import mcp server tools directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..","db-mcp-server"))

from tools.auth import connect_db, disconnect_db
from tools.read import list_databases, list_tables, describe_table, get_db_info, execute_query
from tools.write import preview_query, confirm_execute, cancel_query
from tools.chart import visualize_table

load_dotenv()

# openai client pointing to openrouter
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("base_url"),
)

# model to use - change this to any openrouter model you want
MODEL = "gpt-4o"


# this function calls the actual tool based on tool name
def call_tool(tool_name, args):
    if tool_name == "tool_connect_db":
        return connect_db(args["db_type"], args["host"], args["port"], args["user"], args["password"], args["database"])

    elif tool_name == "tool_disconnect_db":
        return disconnect_db(args["token"])

    elif tool_name == "tool_list_databases":
        return list_databases(args["token"])

    elif tool_name == "tool_list_tables":
        return list_tables(args["token"])

    elif tool_name == "tool_describe_table":
        return describe_table(args["token"], args["table_name"])

    elif tool_name == "tool_get_db_info":
        return get_db_info(args["token"])

    elif tool_name == "tool_execute_query":
        return execute_query(args["token"], args["query"])

    elif tool_name == "tool_preview_query":
        return preview_query(args["token"], args["query"])

    elif tool_name == "tool_confirm_execute":
        # ask user for permission before confirming
        print("\n[AGENT] wants to execute a write query. do you approve? (yes/no): ", end="")
        user_input = input().strip().lower()
        if user_input == "yes":
            return confirm_execute(args["confirmation_id"])
        else:
            return cancel_query(args["confirmation_id"])

    elif tool_name == "tool_cancel_query":
        return cancel_query(args["confirmation_id"])

    elif tool_name == "tool_visualize_table":
        return visualize_table(args["token"], args["query"], args.get("title", "Chart"))

    else:
        return {"success": False, "error": f"unknown tool: {tool_name}"}


# main agent loop
def run_agent():
    print("=== DB Agent ===")
    print("type your question. type 'exit' to quit\n")

    # conversation history
    messages = [
        {
            "role": "system",
            "content": """you are a helpful database agent. you help users connect to databases, explore them, run queries and visualize data.

always follow this flow for write operations:
1. call tool_preview_query first to show the user what will happen
2. wait for user to confirm
3. only then call tool_confirm_execute

for read operations just run them directly.

be concise and helpful. explain query results in simple english."""
        }
    ]

    while True:
        # get user input
        user_input = input("you: ").strip()

        if user_input.lower() == "exit":
            print("bye!")
            break

        if not user_input:
            continue

        # add user message to history
        messages.append({"role": "user", "content": user_input})

        # agent loop - keep calling llm until it stops using tools
        while True:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # add assistant message to history
            messages.append(message)

            # if no tool calls, print response and wait for next user input
            if not message.tool_calls:
                print(f"\nagent: {message.content}\n")
                break

            # handle tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n[calling tool: {tool_name}]")

                # call the actual tool
                result = call_tool(tool_name, args)

                print(f"[tool result: {json.dumps(result, indent=2)[:200]}...]")

                # add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })


if __name__ == "__main__":
    run_agent()