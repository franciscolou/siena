import sqlite3

try:
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # Drop the credentials table if it exists
    cursor.execute("DROP TABLE IF EXISTS credentials")
    print("Table 'credentials' dropped successfully.")

    # Commit the changes and close the connection
    conn.commit()
    print("Changes committed successfully.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("Connection closed.")
