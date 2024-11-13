#!/bin/sh

sudo apt update
sudo apt install docker.io
sudo docker pull kasmweb/chrome:1.16.0

if [ -n "$1" ]; then
    echo "Depoly Docker VNC With Password"
    sudo docker run --rm -d --shm-size=512m -p 6901:6901 -e VNC_PW=$1 kasmweb/chrome:1.16.0
else
    echo "Depoly Docker for No-VNC"
    sudo docker run --rm -d --shm-size=512m -p 6901:6901 kasmweb/chrome:1.16.0
fi
