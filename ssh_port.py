
import sys

from threading import Thread,Lock

from sshtunnel import SSHTunnelForwarder



def backend_thread(ssh_host,ssh_port,ssh_user,ssh_password,remote_port,local_port):
    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        # 如果需要使用私钥认证，替换为以下参数：
        # ssh_private_key="/path/to/private/key",
        remote_bind_address=('localhost', remote_port),
        local_bind_address=('127.0.0.1', local_port)
    )
    dead_lock = Lock()
    dead_lock.acquire()
    dead_lock.acquire()

def run_backend_ssh_redirect(ssh_host,ssh_port,ssh_user,ssh_password,remote_port,local_port):
    thread_imp = Thread(target=backend_thread,args=(ssh_host,ssh_port,ssh_user,ssh_password,remote_port,local_port))
    thread_imp.daemon = True
    thread_imp.start()
