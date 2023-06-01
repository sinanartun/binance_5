#!/bin/bash
cd /home/ec2-user || exit
sudo dnf upgrade -y
sudo dnf -assumeyes groupinstall "Development Tools"
sudo dnf install --assumeyes python3-pip libffi-devel openssl-devel bzip2-devel
git clone https://github.com/sinanartun/binance_5.git
sudo chown -R ec2-user:ec2-user /home/ec2-user/binance_5
sudo chmod 2775 /home/ec2-user/binance_5 && find /home/ec2-user/binance_5 -type d -exec sudo chmod 2775 {} \;
cd binance_5 || exit
python3 -m venv venv
pip3 install -r requirements.txt
python3 main.py