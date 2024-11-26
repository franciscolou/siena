
import datetime

def get_opposite_changes(change):
    switcher = {
        'entrou': ['saiu', 'saiu offline'],
        'saiu': ['entrou'],
        'saiu offline': ['entrou'],
        'perdeu admin': ['tornou-se admin'],
        'tornou-se admin': ['perdeu admin']
    }
    return switcher.get(change)


    # changes = [
    #     OrderedDict([
    #         ("name", row[0]),
    #         ("action", row[1]),
    #         ("date", row[2][:10]),
    #         ("time", row[2][13:])
    #     ])
    #     for row in rows
    # ]

def is_within_x_minutes(table_timestamp, entry_timestamp, x):
    dt_format = "%Y/%m/%d %H:%M:%S"
    dt1 = datetime.strptime(f"{table_timestamp[0]} {table_timestamp[1]}", dt_format)
    dt2 = datetime.strptime(f"{entry_timestamp[0]} {entry_timestamp[1]}", dt_format)
    return abs((dt2 - dt1).total_seconds()) <= x * 60

def is_duplicate(changes, change):
    possible_duplicate_interval = []
    for i in range(len(changes)):
        if changes[i]['name'] == change['name']:
            if changes[i]['name'] == change['action']:                    
                possible_duplicate_interval = changes[i:]
                break
    for i in range(len(possible_duplicate_interval)):
        if possible_duplicate_interval[i]['name'] == change['name']:
            if possible_duplicate_interval[i]['action'] in get_opposite_changes(change['action']):
                return 'sandwich'
    return 'clone'

    