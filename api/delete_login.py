import sys
import sqlite3

def delete_credentials(username):
    # Connect to the database (replace 'your_database.db' with your actual database file)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Delete the credentials from the table
    cursor.execute("DELETE FROM credentials WHERE username = ?", (username,))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_login.py <username>")
        sys.exit(1)

    username = sys.argv[1]

    delete_credentials(username)
    print(f"Usuário {username} deletado.")
