
一键安装节点监控器

```
阿里云:
curl -s -o /tmp/host.py https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/server/host.py ; sudo pip3 install psutil  flask --break-system-packages  --no-deps ; sudo nohup python3 /tmp/host.py HTTPAuthPassword &
腾讯云:
curl -s -o /tmp/host.py https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/server/host.py ; sudo pip3 install psutil  flask ; sudo nohup python3 /tmp/host.py HTTPAuthPassword &
```
