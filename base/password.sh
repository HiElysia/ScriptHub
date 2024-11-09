#!/bin/sh

if [ -z "$1" ]; then
    echo "请提供新密码作为第一个参数。"
    exit 1
fi

username=$(whoami)
new_password=$1

echo "$username:$new_password" | sudo chpasswd
echo "success"
