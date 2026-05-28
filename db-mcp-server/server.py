import argparse
from mcp.server.fastmcp import FastMCP
from tools.auth import connect_db, disconnect_db
from tools.read import list_databases, list_tables, describe_table, get_db_info, execute_query

# create the mcp server
mcp = FastMCP("db-mcp-server")


# --- auth tools ---

@mcp.tool()
def tool_connect_db(db_type: str, host: str, port: int, user: str, password: str, database: str) -> dict:
    """connect to a database. db_type can be sqlite, postgres or mysql. returns a token to use in other tools"""
    return connect_db(db_type, host, port, user, password, database)


@mcp.tool()
def tool_disconnect_db(token: str) -> dict:
    """disconnect from database using the token you got from connect_db"""
    return disconnect_db(token)


# --- read tools ---

@mcp.tool()
def tool_list_databases(token: str) -> dict:
    """list all databases available on the connected server"""
    return list_databases(token)


@mcp.tool()
def tool_list_tables(token: str) -> dict:
    """list all tables in the current database"""
    return list_tables(token)


@mcp.tool()
def tool_describe_table(token: str, table_name: str) -> dict:
    """show columns, data types and constraints of a table"""
    return describe_table(token, table_name)


@mcp.tool()
def tool_get_db_info(token: str) -> dict:
    """get basic info about the database like version and size"""
    return get_db_info(token)


@mcp.tool()
def tool_execute_query(token: str, query: str) -> dict:
    """run a SELECT query and get results. only read only queries allowed here"""
    return execute_query(token, query)


# --- main entry point ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "http"])
    args = parser.parse_args()

    print(f"starting db-mcp-server with transport: {args.transport}")
    mcp.run(transport=args.transport)