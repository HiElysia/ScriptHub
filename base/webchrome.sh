#!/bin/sh

sudo apt update
sudo apt install docker.io
sudo docker pull kasmweb/chrome

if [ -n "$2" ]; then
    echo "Depoly Docker VNC With Password and Chrome Dir"
    mkdir -p $2
    sudo chmod 777 $2
    current_dir=$(dirname "$(realpath "$0")")
    data_dir="$current_dir/$2"
    echo $data_dir

    
    if [ -n "$3" ]; then
        sudo docker run --rm -d --shm-size=1024m -p 6901:6901 -v $data_dir:/home/kasm-user -e VNC_PW=$1 APP_ARGS=--remote-debugging-port=9222 kasmweb/chrome
    else
        sudo docker run --rm -d --shm-size=1024m -p 6901:6901 -v $data_dir:/home/kasm-user -e VNC_PW=$1 kasmweb/chrome
    fi
elif [ -n "$1" ]; then
    echo "Depoly Docker VNC With Password"
    sudo docker run --rm -d --shm-size=1024m -p 6901:6901 -e VNC_PW=$1 kasmweb/chrome
else
    echo "Depoly Docker for No-VNC"
    sudo docker run --rm -d --shm-size=1024m -p 6901:6901 kasmweb/chrome
fi
