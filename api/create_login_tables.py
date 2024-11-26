import sqlite3

try:
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # Create the credentials table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        username TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL
    )
    """)
    print("Table 'credentials' created successfully.")

    # Commit the changes and close the connection
    conn.commit()
    print("Changes committed successfully.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("Connection closed.")
