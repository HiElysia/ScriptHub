
import json
import os
import socket
import sys

from threading import Thread

import paramiko

from tqdm import tqdm


SSH_SUCCESS = 0x00
SSH_AUTH_FAIL = 0x01
SSH_TIMEOUT = 0x02
SSH_UNKNOW = 0xFF


def upload_file_with_ssh(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_file_path,pbar):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=remote_ip, port=remote_port, username=ssh_username, password=ssh_password,timeout=10)

        sftp = client.open_sftp()
        sftp.put(local_file_path, remote_file_path)
    except paramiko.ssh_exception.AuthenticationException:
        pbar.write('upload %s AuthenticationException' % (remote_ip))
        return SSH_AUTH_FAIL
    except paramiko.ssh_exception.SSHException:
        pbar.write('upload %s SSHException' % (remote_ip))
        return SSH_TIMEOUT
    except socket.timeout:
        pbar.write('upload %s Timeout' % (remote_ip))
        return SSH_TIMEOUT
    except:
        pbar.write('upload %s SSH_UNKNOW' % (remote_ip))
        return SSH_UNKNOW

    return SSH_SUCCESS

def download_file_with_ssh(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_file_path,pbar):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=remote_ip, port=remote_port, username=ssh_username, password=ssh_password,timeout=10)

        sftp = client.open_sftp()
        sftp.get(remote_file_path, local_file_path)
        
        sftp.close()
        client.close()
    except paramiko.ssh_exception.AuthenticationException:
        pbar.write('download %s AuthenticationException' % (remote_ip))
        return SSH_AUTH_FAIL
    except paramiko.ssh_exception.SSHException:
        pbar.write('download %s SSHException' % (remote_ip))
        return SSH_TIMEOUT
    except socket.timeout:
        pbar.write('download %s Timeout' % (remote_ip))
        return SSH_TIMEOUT
    except:
        pbar.write('download %s Unknow' % (remote_ip))
        return SSH_UNKNOW

    return SSH_SUCCESS



if __name__ == '__main__':
    if not 5 == len(sys.argv):
        print('Using: python3 up|down local_path remote_path')
        exit()

    sync_mode = sys.argv[1]
    ssh_file_path = sys.argv[2]
    local_path = sys.argv[3]
    remote_path = sys.argv[4]

    if os.path.exists(local_path):
        print('Save Dir Exist')
        exit()

    os.makedirs(local_path)

    try:
        file = open(ssh_file_path)
        data = json.loads(file.read().strip())
        file.close()
    except:
        print('Read SSH File Err')
        exit()
        
    server_list = data.get('servers',[])
    thread_list = []

    with tqdm(total=len(server_list),desc='SSH Sync', unit=' IP') as pbar:
        for server_info in server_list:
            remote_ip = server_info.get('host')
            remote_port = server_info.get('port')
            ssh_username = server_info.get('username')
            ssh_password = server_info.get('password')
            local_file_path = os.path.join(local_path,remote_ip)

            if 'upload' == sync_mode:
                thread_imp = Thread(target=upload_file_with_ssh,args=(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_path,pbar))
            else:
                os.makedirs(local_file_path)
                local_file_path = os.path.join(local_file_path,remote_path.split('/')[-1])
                thread_imp = Thread(target=download_file_with_ssh,args=(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_path,pbar))

            thread_imp.daemon = True
            thread_imp.start()
            thread_list.append(thread_imp)
            pbar.update(1)
            break

    for thread_imp in thread_list:
        thread_imp.join()

    print('Success')
