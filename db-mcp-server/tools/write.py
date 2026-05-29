from db.sessions import sessions

pending_confirmations = {}

import uuid

def get_conn(token):
    if token not in sessions:
        return None, "invalid token. please connect first using connect_db"
    return sessions[token]["conn"], None

def preview_query(token, query):
    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    query_lower = query.strip().lower()
    if query_lower.startswith("select"):
        return {"success": False, "error": "use execute_query for SELECT. this tool is for INSERT, UPDATE, DELETE"}

    if query_lower.startswith("insert"):
        operation = "INSERT"
    elif query_lower.startswith("update"):
        operation = "UPDATE"
    elif query_lower.startswith("delete"):
        operation = "DELETE"
    elif query_lower.startswith("drop"):
        operation = "DROP"
    elif query_lower.startswith("alter"):
        operation = "ALTER"
    elif query_lower.startswith("create"):
        operation = "CREATE"
    else:
        operation = "UNKNOWN"

    confirmation_id = str(uuid.uuid4())

    pending_confirmations[confirmation_id] = {
        "token": token,
        "query": query,
        "operation": operation
    }

    return {
        "success": True,
        "confirmation_id": confirmation_id,
        "operation": operation,
        "query": query,
        "message": f"this will run a {operation} query. call confirm_execute with this confirmation_id to run it. call cancel_query to cancel"
    }

def confirm_execute(confirmation_id):
    if confirmation_id not in pending_confirmations:
        return {"success": False, "error": "confirmation_id not found. maybe it expired or was already used"}

    pending = pending_confirmations[confirmation_id]
    token = pending["token"]
    query = pending["query"]

    conn, err = get_conn(token)
    if err:
        return {"success": False, "error": err}

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()

        del pending_confirmations[confirmation_id]

        return {
            "success": True,
            "message": "query executed successfully",
            "rows_affected": cursor.rowcount
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}

def cancel_query(confirmation_id):
    if confirmation_id not in pending_confirmations:
        return {"success": False, "error": "confirmation_id not found"}

    del pending_confirmations[confirmation_id]
    return {"success": True, "message": "query cancelled successfully"}