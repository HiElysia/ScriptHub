
=====

## 修改IP地址

ip.sh

```
curl -s https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/base/ip.sh | sudo sh -s 192.168.31.15 192.168.31.1
```

====

## 修改主机密码

password.sh

```
curl -s https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/base/password.sh | sudo sh -s ubuntu 1234
```

====

## 启动远程浏览器

安装远程Chrome.sh .参数为VNC密码,VNC用户名是kasm_user

```
直接启动浏览器
curl -s https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/base/webchrome.sh | sudo sh -s root
启动浏览器并且带目录,参数2是指定Chrome的数据目录
curl -s https://raw.githubusercontent.com/HiElysia/ScriptHub/refs/heads/main/base/webchrome.sh | sudo sh -s root chrome_data
```

