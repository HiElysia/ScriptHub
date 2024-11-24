
import csv
import json
import os
import re
import socket
import sys

from threading import Thread

import paramiko

from tqdm import tqdm


SSH_SUCCESS = 0x00
SSH_AUTH_FAIL = 0x01
SSH_TIMEOUT = 0x02
SSH_UNKNOW = 0xFF


def command_with_ssh(remote_ip,remote_port,ssh_username,ssh_password,command,pbar):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=remote_ip, port=remote_port, username=ssh_username, password=ssh_password,timeout=10)
    
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read()
        try:
            output = output.decode('utf-8')
        except:
            output = output.decode('gbk')
        #error = stderr.read().decode('utf-8')
        pbar.write('%s > %s' % (remote_ip,output))

        client.close()
    except paramiko.ssh_exception.AuthenticationException:
        pbar.write('upload %s AuthenticationException' % (remote_ip))
        return SSH_AUTH_FAIL,''
    except paramiko.ssh_exception.SSHException:
        pbar.write('upload %s SSHException' % (remote_ip))
        return SSH_TIMEOUT,''
    except socket.timeout:
        pbar.write('upload %s Timeout' % (remote_ip))
        return SSH_TIMEOUT,''
    #except:
    #    pbar.write('upload %s SSH_UNKNOW' % (remote_ip))
    #    return SSH_UNKNOW,''

    return SSH_SUCCESS,output

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

def help():
    print('Using: python3 up|down ssh_file local_path remote_path')
    print('Using: python3 exec ssh_file command')
    exit()


if __name__ == '__main__':
    if 3 > len(sys.argv):
        help()
        exit()

    sync_mode = sys.argv[1]
    ssh_file_path = sys.argv[2]

    if 'exec' == sync_mode:
        if not 4 == len(sys.argv):
            help()

        command = sys.argv[3]
    else:
        if not 5 == len(sys.argv):
            help()

        local_path = sys.argv[3]
        remote_path = sys.argv[4]

        if os.path.exists(local_path):
            print('Save Dir Exist')
            exit()

        os.makedirs(local_path)

    try:
        try:
            file = open(ssh_file_path, mode='r', encoding='utf-8')
            data = json.loads(file.read().strip())  #  xterminal format
            server_list = data.get('servers',[])
        except:
            file = open(ssh_file_path, mode='r', encoding='utf-8')
            server_list = list(csv.DictReader(file))

        file.close()
    except:
        print('Read SSH File Err')
        exit()
        
    thread_list = []

    with tqdm(total=len(server_list),desc='SSH Sync', unit=' IP') as pbar:
        for server_info in server_list:
            remote_ip = server_info.get('host')
            remote_port = server_info.get('port',22)
            ssh_username = server_info.get('username')
            ssh_password = server_info.get('password')

            if 'up' == sync_mode:
                local_file_path = os.path.join(local_path,remote_ip)
                thread_imp = Thread(target=upload_file_with_ssh,args=(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_path,pbar))
            elif 'down' == sync_mode:
                local_file_path = os.path.join(local_path,remote_ip)
                os.makedirs(local_file_path)
                local_file_path = os.path.join(local_file_path,remote_path.split('/')[-1])
                thread_imp = Thread(target=download_file_with_ssh,args=(remote_ip,remote_port,ssh_username,ssh_password,local_file_path,remote_path,pbar))
            elif 'exec' == sync_mode:
                pattern_variant = r"\{([^\}]+)\}"
                matches = re.findall(pattern_variant, command)
                new_command = command
                
                for variant_name in matches:
                    variant_value = server_info.get(variant_name,'')

                    if not variant_value:
                        continue

                    new_command = new_command.replace('{%s}' % (variant_name),variant_value)
                    
                thread_imp = Thread(target=command_with_ssh,args=(remote_ip,remote_port,ssh_username,ssh_password,new_command,pbar))
            else:
                print('mode error')
                exit()

            thread_imp.daemon = True
            thread_imp.start()
            thread_list.append(thread_imp)
            pbar.update(1)

    for thread_imp in thread_list:
        thread_imp.join()

    print('Success')
