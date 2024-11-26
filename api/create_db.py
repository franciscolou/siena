import sqlite3

# Define the groups
groups = [
    "acesso_a_base",
    "corpo_executivo",
    "corpo_executivo_superior",
    "pracas",
    "oficiais",
    "oficiais_superiores",
    "sala_de_comandos",
    "corredor_interno",
    "direitos",
]

conn = None

try:
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        username TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL
    )
    """)
    print("Table credentials created successfully.")

    # Create tables for each group
    for group in groups:
        # Create members table
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {group} (
            name TEXT PRIMARY KEY NOT NULL,
            isAdmin INTEGER NOT NULL,
            motto TEXT,
            online INTEGER NOT NULL
        )
        """)
        print(f"Table {group} created successfully.")
        
        # Create changes table
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {group}_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        print(f"Table {group}_changes created successfully.")

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {group}_admlog (
            timestamp TEXT PRIMARY KEY NOT NULL,
            adms_online TEXT,
            ref_count INTEGER DEFAULT 0,
            FOREIGN KEY (timestamp) REFERENCES {group}_changes(timestamp) ON DELETE CASCADE
        )
        """)

        print(f"Table {group}_admlog created successfully.")

    # Commit the changes and close the connection
    conn.commit()
    print("Changes committed successfully.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("Connection closed.")

print("Tables created successfully.")
