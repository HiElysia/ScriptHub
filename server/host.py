
import json
import os
import psutil
import sys

from functools import wraps

from flask import *



##  检测服务运行状态

KEEPALIVE_SERVICE = {
    'host': {
        'description': 'Host Service',
        'exec_start': 'python3 /tmp/host.py',
        'exec_user': 'root',
        'env_list': [],
        'work_directory': '/root',
    },
}


def is_sudo():
    return os.geteuid() == 0


class service_template:

    @staticmethod
    def make(description,exec_start,exec_user,env_list,work_directory):
        service_start = ''

        if str == type(exec_start):
            service_start = f'ExecStart={exec_start}\n'
        else:
            for exec_cmd in exec_start:
                service_start += f'ExecStart={exec_cmd}\n'

        service_env = ''
        
        for env in env_list:
            service_env += 'Environment="%s"\n' % (env)

        working_directory = ''

        if work_directory:
            working_directory = f'WorkingDirectory={work_directory}\n' 

        service_template = f'''[Unit]
                            Description={description}

                            [Service]
                            {service_env}
                            {service_start}
                            Restart=always
                            User={exec_user}
                            {working_directory}

                            [Install]
                            WantedBy=multi-user.target
                            '''
        
        return service_template

    @staticmethod
    def get(service_name):
        file_path = f'/etc/systemd/system/{service_name}.service'
        file = open(file_path)
        data = file.read()
        file.close()

        return data

class service_ctl:

    @staticmethod
    def update(service_name,description,exec_start,exec_user,env_list,work_directory):
        if not is_sudo():
            return False
        
        service_template_data = service_template.make(description,exec_start,exec_user,env_list,work_directory)
        
        file_path = f'/etc/systemd/system/{service_name}.service'
        file = open(file_path,'w')
        file.write(service_template_data)
        file.close()

        os.system('systemctl daemon-reload')
        os.system('systemctl enable %s' % (service_name))
        os.system('systemctl start %s' % (service_name))

    @staticmethod
    def reboot(service_name):
        os.system('systemctl daemon-reload')
        os.system('systemctl restart %s' % (service_name))

    @staticmethod
    def stop(service_name):
        os.system('systemctl stop %s' % (service_name))

    @staticmethod
    def is_exist(service_name):
        dir_files = os.listdir('/etc/systemd/system/')
        result = False

        for file_name in dir_files:
            if not file_name.endswith('.service'):
                continue

            if not file_name == '%s.service' % service_name:
                continue

            result = True
            break

        return result

    @staticmethod
    def state(service_name):
        if not is_sudo():
            return 'nosudo'

        data = os.popen('systemctl status %s' % (service_name)).read().split('\n')

        if not data[0]:
            return 'null'
        
        line_data = data[2].strip().split()
        active_state = line_data[2][1:-1]

        if 'Result' in active_state:
            return line_data[1]

        return active_state

    @staticmethod
    def log(service_name):
        if not is_sudo():
            return 'nosudo'

        data = os.popen('journalctl -u %s.service -n 50' % (service_name)).read()

        return data

    @staticmethod
    def log_for_new(service_name):
        if not is_sudo():
            return 'nosudo'

        os.system('journalctl -u %s.service -f' % (service_name))

    @staticmethod
    def setup(service_config):
        if not dict == type(service_config):
            return False
        
        for service_name,service_info in service_config.items():
            if 'running' == service_ctl.state(service_name):
                service_template_data = service_template.make(**service_info)
                service_template_source = service_template.get(service_name)
                
                if service_template_data == service_template_source:
                    continue

            service_info['service_name'] = service_name
            service_ctl.update(**service_info)

        return True


##  获取配置性能

def get_performance():
    cpu_percent = psutil.cpu_percent()
    cpu_count = psutil.cpu_count()
    virtual_memory = psutil.virtual_memory()
    virtual_memory = (virtual_memory.total,virtual_memory.free,virtual_memory.used,virtual_memory.percent)
    disk_usage = psutil.disk_usage('/')
    disk_usage = (disk_usage.total,disk_usage.free,disk_usage.used,disk_usage.percent)
    disk_io_counters = psutil.disk_io_counters()
    disk_io_counters = (disk_io_counters.read_bytes,disk_io_counters.write_bytes)
    net_io_counters = psutil.net_io_counters()
    net_io_counters = (net_io_counters.bytes_recv,net_io_counters.bytes_sent)

    return cpu_count,cpu_percent,virtual_memory,disk_usage,disk_io_counters,net_io_counters


##  后台服务

app = Flask(__name__)

VALID_USERNAME = 'ScriptHub'

if 2 == len(sys.argv):
    VALID_PASSWORD = sys.argv[1]
else:
    print('UnSet HTTP-Auth Password')
    exit()


def check_auth(auth):
    if not auth or not auth.username or not auth.password:
        return False
    return auth.username == VALID_USERNAME and auth.password == VALID_PASSWORD

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not check_auth(auth):
            return jsonify({"message": "Authentication required"}), 401, {
                "WWW-Authenticate": 'Basic realm="Login Required"'
            }
        return f(*args, **kwargs)
    return decorated

@app.route('/get_performance')
@requires_auth
def get_performance_api():
    cpu_count,cpu_percent,virtual_memory,disk_usage,disk_io_counters,net_io_counters = get_performance()

    return jsonify({
        'cpu_count': cpu_count,
        'cpu_percent': cpu_percent,
        'virtual_memory': virtual_memory,
        'disk_usage': disk_usage,
        'disk_io_counters': disk_io_counters,
        'net_io_counters': net_io_counters,
    })

SERVICE_CONFIG_PATH = 'service_config.ini'

def load_service_config():
    try:
        file = open(SERVICE_CONFIG_PATH)
        data = json.loads(file.read())
        file.close()
    except:
        data = {}

    return data

def save_service_config(service_data):
    file = open(SERVICE_CONFIG_PATH,'w')
    file.write(json.dumps(service_data))
    file.close()


@app.route('/add_server',methods=['POST'])
@requires_auth
def add_server():
    '''
    {
        'name': '123',
        'description': 'Host Service',
        'exec_start': 'python3 ./host.py',
        'exec_user': 'root',
        'env_list': [],
        'work_directory': '/root',
    }
    '''
    post_data = request.json()
    server_name = post_data.get('name')
    server_description = post_data.get('description')
    server_exec_start = post_data.get('exec_start')
    server_exec_user = post_data.get('exec_user')
    server_env_list = post_data.get('env_list')
    server_work_directory = post_data.get('work_directory')

    service_ctl.update(server_name,server_description,server_exec_start,server_exec_user,server_env_list,server_work_directory)

    service_config = load_service_config()
    service_config[server_name] = {
        'description': server_description,
        'exec_start': server_exec_start,
        'exec_user': server_exec_user,
        'env_list': server_env_list,
        'work_directory': server_work_directory,
    }
    save_service_config(service_config)

    return jsonify({
        'success': 'ok'
    })

@app.route('/stop_server')
@requires_auth
def stop_server():
    server_name = request.args.get('name')
    
    if not server_name:
        return jsonify({
            'error': 'no server name'
        })

    service_config = load_service_config()

    if not server_name in service_config:
        return jsonify({
            'error': 'not found server'
        })

    service_ctl.stop(server_name)

    return jsonify({
        'success': 'ok'
    })

@app.route('/get_server_state')
@requires_auth
def get_server_state():
    service_config = load_service_config()
    result = {}

    for service_name in service_config.keys():
        service_state = service_ctl.state(service_name)
        result[service_name] = service_state

    return jsonify({
        'state': result
    })

@app.route('/reboot_server')
@requires_auth
def reboot_server():
    server_name = request.args.get('name')
    
    if not server_name:
        return jsonify({
            'error': 'no server name'
        })

    service_config = load_service_config()

    if not server_name in service_config:
        return jsonify({
            'error': 'not found server'
        })

    service_ctl.reboot(server_name)

    return jsonify({
        'success': 'ok'
    })




if __name__ == '__main__':
    service_ctl.setup(KEEPALIVE_SERVICE)

    app.run(host='0.0.0.0',port=57575,
            #ssl_context=('cert.pem', 'key.pem')
            )

