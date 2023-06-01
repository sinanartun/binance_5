#!/bin/bash
cd /home/ec2-user || exit
sudo yum upgrade -y
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel bzip2-devel libffi-devel
/usr/bin/python3 -m pip install --upgrade pip
cd /home/ec2-user || exit
git clone https://github.com/sinanartun/binance_5.git
sudo chown -R ec2-user:ec2-user /home/ec2-user/binance_5
sudo chmod 2775 /home/ec2-user/binance_5 && find /home/ec2-user/binance_5 -type d -exec sudo chmod 2775 {} \;
cd binance_5 || exit
python3 -m venv venv
pip3 install -r requirements.txt
sudo tee /etc/systemd/system/binance.service << EOF
[Unit]
Description=Binance Service

[Service]
User=root
ExecStart=/usr/bin/python3 /home/ec2-user/binance_5/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable binance
sudo systemctl start binance
