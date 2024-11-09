#!/bin/sh

sudo apt update
sudo apt install -y docker.io jq
sudo mkdir -p /etc/systemd/system/docker.service.d/

if [ -n "$1" ]; then
    sudo echo -e "[Service]\nEnvironment=\"HTTP_PROXY=$1\"\nEnvironment=\"HTTPS_PROXY=$1\"\n" | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null
fi

sudo systemctl daemon-reload
sudo systemctl restart docker
sudo docker pull nillion/verifier:v1.0.1
sudo mkdir -p nillion/verifier

FILE="nillion/verifier/credentials.json"

if [ ! -e "$FILE" ]; then
    sudo docker run -v ./nillion/verifier:/var/tmp nillion/verifier:v1.0.1 initialise
fi

echo 'address :'
jq -r '.address' nillion/verifier/credentials.json
echo 'pubkey :'
jq -r '.pub_key' nillion/verifier/credentials.json