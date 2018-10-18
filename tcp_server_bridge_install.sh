#!/bin/bash
source ./tcp_server_bridge.cfg

echo "Creating TCP Server Bridge Directory"
rm -rf $TCP_SERVER_BRIDGE_DIR
mkdir $TCP_SERVER_BRIDGE_DIR

echo "Copy the python file"
cp ./$TCP_SERVER_BRIDGE_FILE $TCP_SERVER_BRIDGE_DIR


echo "Create and copy ESD CFG File"
touch ./$TCP_SERVER_BRIDGE_CFG
echo "esdIP=$TCP_SERVER_BRIDGE_CFG_ESD_IP" >> ./$TCP_SERVER_BRIDGE_CFG
echo "pathABC=$TCP_SERVER_BRIDGE_CFG_ESD_DIR" >> ./$TCP_SERVER_BRIDGE_CFG
echo "port=$TCP_SERVER_BRIDGE_CFG_ESD_PORT" >> ./$TCP_SERVER_BRIDGE_CFG
echo "retries=$TCP_SERVER_BRIDGE_CFG_ESD_RETRIES" >> ./$TCP_SERVER_BRIDGE_CFG
cp ./$TCP_SERVER_BRIDGE_CFG $TCP_SERVER_BRIDGE_DIR




echo "Creating the service user"
useradd -r -s /bin/false $TCP_SERVER_BRIDGE_USER
chown -R $TCP_SERVER_BRIDGE_USER:$TCP_SERVER_BRIDGE_USER $TCP_SERVER_BRIDGE_DIR

echo "Creating the service file"
rm -f $TCP_SERVER_BRIDGE_SERVICE
touch $TCP_SERVER_BRIDGE_SERVICE

echo "[Unit]" >> $TCP_SERVER_BRIDGE_SERVICE
echo "Description=Tevin TCP Server Bridge" >> $TCP_SERVER_BRIDGE_SERVICE
echo "After=syslog.target" >> $TCP_SERVER_BRIDGE_SERVICE
echo "" >> $TCP_SERVER_BRIDGE_SERVICE
echo "[Service]" >> $TCP_SERVER_BRIDGE_SERVICE
echo "Type=simple" >> $TCP_SERVER_BRIDGE_SERVICE
echo "User=$TCP_SERVER_BRIDGE_USER" >> $TCP_SERVER_BRIDGE_SERVICE
echo "Group=$TCP_SERVER_BRIDGE_USER" >> $TCP_SERVER_BRIDGE_SERVICE
echo "WorkingDirectory=$TCP_SERVER_BRIDGE_DIR" >> $TCP_SERVER_BRIDGE_SERVICE
echo "ExecStart=$TCP_SERVER_BRIDGE_DIR/$TCP_SERVER_BRIDGE_FILE" >> $TCP_SERVER_BRIDGE_SERVICE
echo "SyslogIdentifier=$SYSLOGID" >> $TCP_SERVER_BRIDGE_SERVICE
echo "StandardOutput=syslog" >> $TCP_SERVER_BRIDGE_SERVICE
echo "StandardError=syslog" >> $TCP_SERVER_BRIDGE_SERVICE
echo "Restart=always" >> $TCP_SERVER_BRIDGE_SERVICE
echo "RestartSec=3" >> $TCP_SERVER_BRIDGE_SERVICE
echo "" >> $TCP_SERVER_BRIDGE_SERVICE
echo "[Install]" >> $TCP_SERVER_BRIDGE_SERVICE
echo "WantedBy=multi-user.target" >> $TCP_SERVER_BRIDGE_SERVICE

echo ""
echo "Installation done"
echo ""
echo "enabling and starting the service: systemctl enable $SYSLOGID && systemctl start $SYSLOGID"
systemctl enable $SYSLOGID
systemctl start $SYSLOGID

echo "Service status:"
systemctl status $SYSLOGID


echo "Finish"
