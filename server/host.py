
import os
import psutil

from flask import *



##  检测服务运行状态

'''
KEEPALIVE_SERVICE = {
    'tg_bot': {
        'description': 'TG Bot Service',
        'exec_start': 'python3 ./tg_bot_server.py',
        'exec_user': 'ubuntu',
        'env_list': [],
        'work_directory': '/home/ubuntu/project_meme/tg_bot_api',
    },
}
'''


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

print(dir(psutil))
print(psutil.cpu_percent())
print(psutil.cpu_count())
print(psutil.virtual_memory())
print(psutil.disk_usage('/'))
print(psutil.disk_io_counters())
print(psutil.net_io_counters())

if __name__ == '__main__':
    pass

