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
GATEWAY=$2

network_config=$(cat <<EOF
network:
    ethernets:
        ens33:
            dhcp4: no
            addresses: [$IP_ADDRESS/24]
            gateway4: $GATEWAY
            nameservers:
                addresses: [$GATEWAY]
    version: 2
EOF
)


sudo echo -e $network_config | sudo tee /etc/netplan/50-cloud-init.yaml > /dev/null
sudo netplan apply
