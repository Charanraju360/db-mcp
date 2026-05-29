import uuid
from db.connector import make_connection
from db.sessions import sessions

# connect_db tool
def connect_db(db_type, host, port, user, password, database):
    try:
        conn = make_connection(db_type, host, port, user, password, database)

        token = str(uuid.uuid4())

        sessions[token] = {
            "conn": conn,
            "db_type": db_type,
            "database": database
        }

        return {"success": True, "token": token, "message": f"connected to {db_type} database: {database}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# disconnect_db tool
def disconnect_db(token):
    if token not in sessions:
        return {"success": False, "error": "token not found. maybe already disconnected"}

    try:
        sessions[token]["conn"].close()
        del sessions[token]
        return {"success": True, "message": "disconnected successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}