from db.sessions import sessions

# helper to get connection from token
def get_conn(token):
    if token not in sessions:
        return None, "invalid token. please connect first using connect_db"
    return sessions[token]["conn"], None


# list all databases on the server
def list_databases(token):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    db_type = sessions[token]["db_type"]

    try:
        cursor = conn.cursor()

        if db_type == "postgres":
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        elif db_type == "mysql":
            cursor.execute("SHOW DATABASES")
        elif db_type == "sqlite":
            # sqlite is a single file, no concept of multiple databases
            return {"success": True, "databases": [sessions[token]["database"]]}

        rows = cursor.fetchall()
        databases = [row[0] for row in rows]
        return {"success": True, "databases": databases}

    except Exception as e:
        return {"success": False, "error": str(e)}

# list all tables in current database
def list_tables(token):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    db_type = sessions[token]["db_type"]

    try:
        cursor = conn.cursor()

        if db_type == "postgres":
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        elif db_type == "mysql":
            cursor.execute("SHOW TABLES")
        elif db_type == "sqlite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

        rows = cursor.fetchall()
        tables = [row[0] for row in rows]
        return {"success": True, "tables": tables}

    except Exception as e:
        return {"success": False, "error": str(e)}


# describe a single table - shows columns, types, nullable etc
def describe_table(token, table_name):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    db_type = sessions[token]["db_type"]

    try:
        cursor = conn.cursor()

        if db_type == "postgres":
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            rows = cursor.fetchall()
            columns = [{"column": r[0], "type": r[1], "nullable": r[2], "default": r[3]} for r in rows]

        elif db_type == "mysql":
            cursor.execute(f"DESCRIBE `{table_name}`")
            rows = cursor.fetchall()
            columns = [{"column": r[0], "type": r[1], "nullable": r[2], "key": r[3], "default": r[4]} for r in rows]

        elif db_type == "sqlite":
            cursor.execute(f"PRAGMA table_info({table_name})")
            rows = cursor.fetchall()
            columns = [{"column": r[1], "type": r[2], "nullable": "NO" if r[3] else "YES", "default": r[4]} for r in rows]

        return {"success": True, "table": table_name, "columns": columns}

    except Exception as e:
        return {"success": False, "error": str(e)}


# get basic info about the database
def get_db_info(token):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    db_type = sessions[token]["db_type"]

    try:
        cursor = conn.cursor()
        info = {"db_type": db_type, "database": sessions[token]["database"]}

        if db_type == "postgres":
            cursor.execute("SELECT version()")
            info["version"] = cursor.fetchone()[0]
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            info["size"] = cursor.fetchone()[0]

        elif db_type == "mysql":
            cursor.execute("SELECT VERSION()")
            info["version"] = cursor.fetchone()[0]

        elif db_type == "sqlite":
            cursor.execute("SELECT sqlite_version()")
            info["version"] = cursor.fetchone()[0]

        return {"success": True, "info": info}

    except Exception as e:
        return {"success": False, "error": str(e)}


# run a read only select query
def execute_query(token, query):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    # basic safety check - only allow SELECT
    if not query.strip().lower().startswith("select"):
        return {"success": False, "error": "only SELECT queries allowed here. use execute_write for other operations"}

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        # get column names
        columns = [desc[0] for desc in cursor.description]

        return {"success": True, "columns": columns, "rows": rows, "count": len(rows)}

    except Exception as e:
        return {"success": False, "error": str(e)}