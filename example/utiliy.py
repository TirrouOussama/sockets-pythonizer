import sqlite3
import os


def create_creds_db():
    conn = sqlite3.connect("op_creds.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS op_creds (
            mac TEXT,
            password TEXT,
            email TEXT,
            phone TEXT,
            token TEXT,
            expiry TEXT
        )
    """
    )
    conn.commit()
    conn.close()


create_creds_db()


def insert_creds(password, email, phone, mac="", token="", expiry="None"):
    try:
        conn = sqlite3.connect("op_creds.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO op_creds (mac, password, email, phone, token)
            VALUES (?, ?, ?, ?, ?)
        """,
            (mac, password, email, phone, token),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] insert_creds failed: {e}")
        return False


# insert_creds(
#     password="example-password",
#     email="example-email@gmail.com",
#     phone="None",
#     mac="None",
#     token="",
#     expiry="None",
# )
def create_passcode_db():
    conn = sqlite3.connect("op_passcodes.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS passcode_table (
            mac TEXT,
            ip TEXT,
            phone TEXT,
            email TEXT,
            passcode TEXT,
            expiry TEXT
        )
    """
    )

    conn.commit()
    conn.close()


def create_local_auth_db():
    # Ensure the folder exists
    if not os.path.exists("databases"):
        os.makedirs("databases")

    # Connect to database
    conn = sqlite3.connect("databases/local_auth.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS local_auth (
            token TEXT
        )
    """
    )

    # Ensure at least one row exists
    cursor.execute("SELECT COUNT(*) FROM local_auth")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO local_auth (token) VALUES (?)", ("",))

    conn.commit()
    conn.close()

    print("Database local_auth.db ready with one row in 'local_auth' table.")


# Call the function
create_local_auth_db()
