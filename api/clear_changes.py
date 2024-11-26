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


# Connect to the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Iterate over each group and delete all elements from "{group}_changes"
for group in groups:
    table_name = f"{group}_changes"
    cursor.execute(f"DELETE FROM {table_name}")
    print(f"Deleted all elements from {table_name}.")

# Commit the changes and close the connection
conn.commit()
conn.close()