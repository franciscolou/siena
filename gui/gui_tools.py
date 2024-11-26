import requests
from datetime import datetime
import os
import sys
###########################################################
######################### UTILS ###########################
###########################################################

date_displays = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

def get_formatted_datetime_now():
    current_time = datetime.now()
    today_date = current_time.date()
    now_time = current_time.strftime('%H:%M:%S')
    year = today_date.strftime('%Y')
    month = date_displays[int(today_date.strftime('%m')) - 1]
    day = today_date.strftime('%d')
    return f"{day} {month} {year} - {now_time}"

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
    ("sala_de_comandos", ID_SALA_DE_COMANDOS, '[DIC] Sala de Comandos', '[DIC] S. de Comandos ®', '#dcdcdc'),
    ("corredor_interno", ID_CORREDOR_INTERNO, '[DIC] Corredor Interno ®', '[DIC] Corredor Interno ®', '#202020'),
    ("direitos", ID_DIREITOS, '[DIC] Direitos ®', '[DIC] Direitos ®', '#c6d4da')
]


def find_group_index(group):
    for i in range(len(groups)):
        if group == groups[i][0]:
            return i

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def generate_clipboard_text(group_name, admlog, timestamp):
    clipboard_text = f'{group_name} | Registro de administradores\n\n'
    formatted_timestamp = datetime.strptime(timestamp, '%Y-%m-%d - %H:%M:%S').strftime('%d/%m/%Y - %H:%M:%S')
    clipboard_text += f'[ {formatted_timestamp} ]\n\n'
    admlog = admlog[(admlog.find('\n')+1):]
    admlog_lines = admlog.split('\n')
    for line in admlog_lines:
        clipboard_text += f'- {line}\n'
    return clipboard_text

def ntorole(n):
    switcher = {
        1: "Usuário",
        2: "Moderador",
        3: "Administrador",
    }
    return switcher.get(n, "Invalid role")

        
###########################################################
###########################################################



###########################################################
############### SERVER AND API INTERACTION ################
###########################################################

def get_group_members(group_name: str):
    group_id = groups[find_group_index(group_name)][1]
    _url = f'https://www.habbo.com.br/api/public/groups/{group_id}/members'
    request = requests.get(_url)

    group_members_list = []

    for member in request.json():
        group_members_list.append(
            {
                'name': member['name'].strip(),
                'motto': member['motto'],
                'isAdmin': member['isAdmin'],
                'online': member['online']
            }
        )

    # print(group_members_list)

    return group_members_list

def get_group_changes(group: str):
    _url = f'http://152.67.44.128:5000/{group}/changes'
    # _url = f'http://127.0.0.1:5000/{group}/changes'
    request = requests.get(_url)

    group_changes_list = []

    for change in request.json():
        group_changes_list.append(
            {
                'name': change['name'].strip(), 
                'action': change['action'],
                'date': change['date'],
                'time': change['time']
            }
        )

    return group_changes_list

def validate_credentials(username: str, password: str):
    _url = 'http://152.67.44.128:5000/login'
    headers = {
        'x-api-key': 'oP8n9vE7pQ4L6rT1kY2cX3wM0zB5fH9dN7gV4aU8jP2qS3xW6lR1mC8oJ3',
        'Content-Type': 'application/json'
    }
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(_url, json=data, headers=headers)
    if response.status_code == 200:
        return 1
    else:
        return 0
    
def get_admlog(group_name, timestamp):
    _url = f"http://152.67.44.128:5000/{group_name}/admlog/{timestamp}"
    # _url = f'http://127.0.0.1:5000/{group_name}/admlog/{timestamp}'
    request = requests.get(_url)

    admlogs_list = request.json().get('adms_online')

    return admlogs_list

    

###########################################################
###########################################################



