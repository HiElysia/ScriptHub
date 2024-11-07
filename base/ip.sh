#!/bin/sh


if [ $# -lt 2 ]; then
    echo "Using: sudo ip.sh 192.168.31.131 192.168.31.1"
    exit
fi

#  curl -s http://xxx.sh | sh -s arg1 arg2 arg3

INTERFACE=$(ip -o -4 addr show up | awk '$2 ~ /^ens/ {print $2}')

if [ -z "$HTTP_PROXY" ]; then
    INTERFACE=$(ip -o -4 addr show up | awk '$2 ~ /^eth/ {print $2}')
fi

IP_ADDRESS=$1
NETMASK="255.255.255.0"
GATEWAY=$2

# 设置 IP 地址和子网掩码
sudo ifconfig "$INTERFACE" "$IP_ADDRESS" netmask "$NETMASK"

# 设置网关
sudo route add default gw "$GATEWAY" "$INTERFACE"

# 显示设置后的网络配置信息
echo "IP 地址设置成功:"
ifconfig "$INTERFACE"
route -n

