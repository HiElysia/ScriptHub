
import csv
import json
import secrets
import sys


def make_id():
    random_bytes = secrets.token_bytes(24)
    return '672c86' + random_bytes.hex()[:18]

def make_group(group_name):
    group_id = make_id()
    return {"name":group_name,"_id":group_id,"createdAt":"2024-11-04T16:48:59+08:00","updatedAt":"2024-11-04T16:48:59+08:00"},group_id

def make_ip(group_id,title,ip,user,password):
    return {"groupId":group_id,"title":title,"host":ip,"port":22,"authType":"password","connectionConfig":{"connectOptions":{"algorithms":{}},"init":{}},"username":user,"password":password,"_id":make_id(),"createdAt":"2024-11-04T16:50:55+08:00","updatedAt":"2024-11-04T16:50:55+08:00"}


if __name__ == '__main__':
    if not 3 == len(sys.argv):
        print('Using: python3 ./xterminal_group_maker.py GroupName data.csv')
        print('  data.csv')
        print('     ip,username,password')
        print('     192.168.1.2,root,root')
        print('     192.168.1.3,root,root')
        print('     ....')
        exit()

    group_name = sys.argv[1]
    file_path = sys.argv[2]

    group_json,group_id = make_group(group_name)
    server_list = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            ip = row.get('ip','')
            username = row.get('username','')
            password = row.get('password','')
            
            if not ip or not username or not password:
                continue

            server_list.append(make_ip(group_id,ip,ip,username,password))

    data = json.dumps({
        'groups':[
            group_json
        ],
        'servers': server_list
    })
    
    file = open('sshimport-%s.json' % (group_name),'w')
    file.write(data)
    file.close()

