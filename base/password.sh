#!/bin/sh

if [ -z "$1" ]; then
    echo "请提供新密码作为第一个参数。"
    exit 1
fi

username=$(whoami)
new_password=$1

sudo chpasswd <<< "$username:$new_password"
echo "success"
