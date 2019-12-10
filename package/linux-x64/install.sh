!#/usr/bin/bash

SERVICE_NAME='electionguard-api.service'

echo "stopping ElectionGuard services"
sudo systemctl stop $SERVICE_NAME
sudo systemctl disable $SERVICE_NAME
sudo rm -rf /etc/systemd/system/$SERVICE_NAME

if [ ! -d "/bin/electionguard" ]; then
        sudo mkdir /bin/electionguard
fi
    
sudo rm -rf /bin/electionguard/*

sudo tar -zxvf electionguard-api.tar.gz -C /bin/electionguard/

sudo chmod -R 777 /bin/electionguard

sudo cp /bin/electionguard/$SERVICE_NAME /etc/systemd/system/$SERVICE_NAME

echo "reloading services"
sudo systemctl daemon-reload
sudo systemctl reset-failed

echo "enabling services"
sudo systemctl enable $SERVICE_NAME

echo "starting ElectionGuard services"
sudo systemctl start $SERVICE_NAME
systemctl status $SERVICE_NAME

echo "done"