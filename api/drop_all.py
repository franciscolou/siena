import sqlite3

def drop_all_tables_and_triggers(database_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        print("Connected to the database successfully.")

        # Query to get the list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Drop each table except sqlite_sequence
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence' and table_name != 'credentials':
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"Table {table_name} dropped successfully.")
            else:
                print(f"Skipping internal table {table_name}.")

        # Query to get the list of all triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = cursor.fetchall()

        # Drop each trigger
        for trigger in triggers:
            trigger_name = trigger[0]
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
            print(f"Trigger {trigger_name} dropped successfully.")

        # Commit the changes and close the connection
        conn.commit()
        print("All tables and triggers dropped successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

# Example usage
database_path = 'database.db'
drop_all_tables_and_triggers(database_path)