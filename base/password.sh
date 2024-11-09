#!/bin/sh

if [ -z "$2" ]; then
    echo "请提供用户名和新密码。"
    exit 1
fi

username=$1
new_password=$2

echo "$username:$new_password" | sudo chpasswd
echo "success"
