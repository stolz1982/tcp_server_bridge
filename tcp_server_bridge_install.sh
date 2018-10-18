#!/bin/bash
source ./tcp_server_bridge.cfg






echo "Creating the user file"
rm -rf ./tcp_server_bridge.service
touch ./

echo "[Unit]" >> 
Description=Tevin TCP Server Bridge
After=syslog.target

[Service]
Type=simple
User=$TCP_SERVER_BRIDGE_USER
Group=$TCP_SERVER_BRIDGE_USER
WorkingDirectory=$TCP_SERVER_BRIDGE_DIR
ExecStart=$TCP_SERVER_BRIDGE_DIR/$TCP_SERVER_BRIDGE_FILE
SyslogIdentifier=$SYSLOGID
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target 


