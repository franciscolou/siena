import requests
import sqlite3
import time
import json
from queue import Queue
from flask import Flask, jsonify, Response, request
import datetime
import threading
import logging
import sys
from werkzeug.serving import is_running_from_reloader
from collections import OrderedDict
from pytz import timezone
from dotenv import load_dotenv
import os

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')

# Initialize a connection pool
def init_connection_pool(size):
    pool = Queue(maxsize=size)
    for _ in range(size):
        conn = sqlite3.connect('database.db', check_same_thread=False, timeout=10)  # Replace with your actual database connection
        pool.put(conn)
    return pool

connection_pool = init_connection_pool(size=15)  # Adjust the pool size as needed

# Configure logging
logging.basicConfig(level=logging.INFO)

ID_OFICIAIS = 'g-hhbr-247773992b2ed79b8f00e564abad2c43'
ID_OFICIAIS_SUPERIORES = 'g-hhbr-7b5c62e80d30cd30f003eab08555a124'
ID_PRACAS = 'g-hhbr-e45543b627d203d8caf1a4476bb42fab'
ID_CORPO_EXECUTIVO = 'g-hhbr-da0cd92560170f5d42d0e59dd6dbc268'
ID_CORPO_EXECUTIVO_SUPERIOR = 'g-hhbr-7f9e61c9ce3700323d870bf420732535'
ID_ACESSO_A_BASE = 'g-hhbr-d23226b5786b954f457a4dbf58fcc6ca'
ID_SALA_DE_COMANDOS = 'g-hhbr-d0bd6c9deb81c3a5782ff137447c52ed'
ID_CORREDOR_INTERNO = 'g-hhbr-26acd7eedc1dfbb9dbfde33661b8641f'
ID_DIREITOS = 'g-hhbr-447f4f9536e7043f0a4e6d8a2a135ffb'

groups = [
    ("acesso_a_base", ID_ACESSO_A_BASE, '[DIC] Acesso à Base ®', '[DIC] Acesso à Base ®', '#ff3333'),
    ("corpo_executivo", ID_CORPO_EXECUTIVO, '[DIC] Corpo Executivo ®', '[DIC] Corpo Executivo ®', '#ededed'),
    ("corpo_executivo_superior", ID_CORPO_EXECUTIVO_SUPERIOR, '[DIC] Corpo Executivo Superior ®', '[DIC] CE Superior ®', '#cfcfcf'),
    ("pracas", ID_PRACAS, '[DIC] Praças ®', '[DIC] Praças ®', '#0acf02'),
    ("oficiais", ID_OFICIAIS, '[DIC] Oficiais ®', '[DIC] Oficiais ®', '#fc5b5b'),
    ("oficiais_superiores", ID_OFICIAIS_SUPERIORES, '[DIC] Oficiais Superiores ®', '[DIC] Ofc. Superiores ®', '#fbc900'),
    ("sala_de_comandos", ID_SALA_DE_COMANDOS, '[DIC] Sala de Comandos', '[DIC] Sala de Comandos ®', '#dcdcdc'),
    ("corredor_interno", ID_CORREDOR_INTERNO, '[DIC] Corredor Interno ®', '[DIC] Corredor Interno ®', '#202020'),
    ("direitos", ID_DIREITOS, '[DIC] Direitos ®', '[DIC] Direitos ®', '#c6d4da')
]


# Get a connection from the pool
def get_connection(pool):
    rtr = pool.get()
    # print(f"Connection taken. Size of the queue: {pool.qsize()}")
    print(datetime.datetime.now().time())
    return rtr

# Return a connection to the pool
def return_connection(pool, conn):
    # print(f"Size of the queue before returning: {pool.qsize()}")
    pool.put(conn)
    # print(f"Connection returned. Size of the queue: {pool.qsize()}")

# Fetch data from the API
def fetch_members_from_api(group_id):
    response = requests.get(f'https://www.habbo.com.br/api/public/groups/{group_id}/members')
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def find_member_by_name(name, lst):
    for element in lst:
        if element['name'] == name:
            return element
# Calculate changes
def calculate_changes(last_members, old_members):
    # Define the timezone for Brazil
    br_tz = timezone('America/Sao_Paulo')

    # Get the current time in the specified timezone
    current_time = datetime.datetime.now(br_tz)
    now_timestamp = f"{current_time.date()} - {current_time.strftime('%H:%M:%S')}"
    old_members_ids = {member['name'] for member in old_members}
    last_members_ids = {member['name'] for member in last_members}
    members_that_left_ids = old_members_ids - last_members_ids
    new_members_ids = last_members_ids - old_members_ids

    members_got_adm_dicts = []
    members_lost_adm_dicts = []

    for member_name in last_members_ids:
        last_member = find_member_by_name(member_name, last_members)
        old_member = find_member_by_name(member_name, old_members)
        
        if last_member.get("isAdmin") and (not old_member or not old_member.get('isAdmin')):
            members_got_adm_dicts.append({
                "name": last_member['name'],
                "action": "tornou-se admin",
                "timestamp": now_timestamp
            })
        elif not last_member.get('isAdmin') and (old_member and old_member.get('isAdmin')):
            members_lost_adm_dicts.append({
                "name": last_member['name'],
                "action": "perdeu admin",
                "timestamp": now_timestamp
            })

    members_that_left_dicts = []
    new_members_dicts = []

    for member_name in members_that_left_ids:
        old_member = find_member_by_name(member_name, old_members)
        action = "saiu" if old_member['online'] else "saiu offline"
        members_that_left_dicts.append({
            "name": member_name,
            "action": action,
            "timestamp": now_timestamp
        })

    for member_name in new_members_ids:
        new_members_dicts.append({
            "name": member_name,
            "action": "entrou",
            "timestamp": now_timestamp
        })
    changes = members_that_left_dicts + new_members_dicts + members_got_adm_dicts + members_lost_adm_dicts
    return changes

# Update the database
def update_database(conn, group_name, changes, last_members, old_members):
    cursor = conn.cursor()

    # Update changes table
    if changes:
        for change in changes:
            cursor.execute(
            f"""
            INSERT INTO {group_name}_changes (name, action, timestamp) 
            VALUES (?, ?, ?)
            """, 
            (change['name'], change['action'], change['timestamp'])
            )

        # Insert old members who are admins into the admlog table
        adms_online = [member['name'] for member in old_members if member.get('isAdmin') and member.get('online')]
        cursor.execute(
            f"""
            INSERT INTO {group_name}_admlog (timestamp, adms_online)
            VALUES (?, ?)
            """,
            (changes[0]['timestamp'], json.dumps(adms_online))
        )

    # Update members table
    cursor.execute(f"DELETE FROM {group_name}")

    for member in last_members:
        cursor.execute(
            f"""
            INSERT INTO {group_name} (name, isAdmin, motto, online)
            VALUES (?, ?, ?, ?)
            """,
            (member['name'], member['isAdmin'], member['motto'], member['online'])
        )

    # Commit the transaction
    conn.commit()

    # Query the changes table to verify the insertion
    cursor.execute(f"SELECT * FROM {group_name}_changes")
    changes_result = cursor.fetchall()
    cursor.execute(f"SELECT * FROM {group_name}_admlog")

    # Update members table
    cursor.execute(f"DELETE FROM {group_name}")
    for member in last_members:
        cursor.execute(
            f"""
            INSERT INTO {group_name} (name, isAdmin, motto, online)
            VALUES (?, ?, ?, ?)
            """,
            (member['name'], member['isAdmin'], member['motto'], member['online'])
        )

    conn.commit()
    cursor.execute(f"SELECT * FROM {group_name}_changes")
    cursor.close()

# Job to be scheduled
def job(pool, group_name, group_id):
    print(f"Checking {group_name}...")
    start_time = time.time()
    try:
        last_members = fetch_members_from_api(group_id)
        conn = get_connection(pool)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {group_name}")
        old_members = [
            {
                "name": member[0],
                "isAdmin": member[1],
                "motto": member[2],
                "online": member[3]
            }
            for member in cursor.fetchall()]

        changes = calculate_changes(last_members, old_members)
        update_database(conn, group_name, changes, last_members, old_members)
    except Exception as e:
        logging.error(f"Error in job for group {group_name}: {e}")
    finally:
        elapsed_time = time.time() - start_time
        print(f"Updated {group_name} in {elapsed_time:.3f}ms.")
        return_connection(pool, conn)

def job_loop(pool, group_name, group_id, stop_event):
    try:
        while not stop_event.is_set():
            job(pool, group_name, group_id)
            stop_event.wait(30) 
    except Exception as e:
        logging.error(f"Error in job loop for group {group_name}: {e}")

# Initialize the connection pool
def main():
    global connection_pool

    stop_events = {}

    for group in groups:
        stop_event = threading.Event()
        stop_events[group[0]] = stop_event
        thread = threading.Thread(target=job_loop, args=(connection_pool, group[0], group[1], stop_event))
        thread.start()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

@app.route('/<group_name>/members', methods=['GET'])
def get_group_data(group_name):
    global connection_pool
    conn = get_connection(connection_pool)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, motto, isAdmin, online FROM {group_name}")
    rows = cursor.fetchall()
    return_connection(connection_pool, conn)

    # Convert list of tuples to list of dictionaries
    members = [
        OrderedDict([
            ("name", row[0]),
            ("motto", row[1]),
            ("isAdmin", row[2]),
            ("online", row[3])
        ])
        for row in rows
    ]
    return Response(json.dumps(members, sort_keys=False), mimetype='application/json')

@app.route('/<group_name>/changes', methods=['GET'])
def get_group_changes(group_name):
    global connection_pool
    conn = get_connection(connection_pool)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, action, timestamp FROM {group_name}_changes")
    rows = cursor.fetchall()
    return_connection(connection_pool, conn)
    
    # Convert list of tuples to list of dictionaries
    changes = [
        OrderedDict([
            ("name", row[0]),
            ("action", row[1]),
            ("date", row[2][:10]),
            ("time", row[2][13:])
        ])
        for row in rows
    ]
    return Response(json.dumps(changes, sort_keys=False), mimetype='application/json')

def check_api_key(key):
    return key == API_KEY

@app.route('/<group_name>/admlog/<timestamp>', methods=['GET'])
def get_group_admlog(group_name, timestamp):
    global connection_pool
    conn = get_connection(connection_pool)
    cursor = conn.cursor()
    
    # Execute the query to fetch the adms_online column for the given timestamp
    cursor.execute(f"SELECT adms_online FROM {group_name}_admlog WHERE timestamp = '{timestamp}'")
    adms_online = cursor.fetchone()
    
    # Check if a result was returned
    if not adms_online:
        return_connection(connection_pool, conn)
        return jsonify({'error': 'Log not found'}), 404
    
    # Deserialize the JSON string to a Python list
    adms_online_list = json.loads(adms_online[0])
    
    return_connection(connection_pool, conn)
    
    # Return the list as a JSON response
    return jsonify({'adms_online': adms_online_list}), 200

@app.route('/login', methods=['POST'])
def login():
    api_key = request.headers.get('x-api-key')
    if not check_api_key(api_key):
        return jsonify({'error': 'Unauthorized access'}), 401

    global connection_pool
    conn = get_connection(connection_pool)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT username, password FROM credentials 
        WHERE username = '{request.json.get('username')}' AND password = '{request.json.get('password')}'
    """)
    login_successful = cursor.fetchall()
    return_connection(connection_pool, conn)
    
    if not login_successful:
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    if not is_running_from_reloader():
        main()
    app.run(host="0.0.0.0", debug=True)