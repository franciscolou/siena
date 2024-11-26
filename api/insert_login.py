import sys
import sqlite3

def insert_credentials(username, password):
    # Connect to the database (replace 'your_database.db' with your actual database file)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert the credentials into the table
    cursor.execute("INSERT INTO credentials (username, password) VALUES (?, ?)", (username, password))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python insert_login.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    insert_credentials(username, password)
    print(f"Usuário {username} com senha {password} cadastrado.")