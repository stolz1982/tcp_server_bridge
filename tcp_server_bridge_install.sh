#!/bin/bash
source ./tcp_server_bridge.cfg

systemctl stop $SYSLOGID

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
SERVICE_FILE=$TCP_SERVER_BRIDGE_SERVICE_DIR/$SYSLOGID.service
rm -f $SERVICE_FILE
touch $SERVICE_FILE

echo "[Unit]" >> $SERVICE_FILE
echo "Description=Tevin TCP Server Bridge" >> $SERVICE_FILE
echo "After=syslog.target" >> $SERVICE_FILE
echo "" >> $SERVICE_FILE
echo "[Service]" >> $SERVICE_FILE
echo "Type=simple" >> $SERVICE_FILE
echo "User=$TCP_SERVER_BRIDGE_USER" >> $SERVICE_FILE
echo "Group=$TCP_SERVER_BRIDGE_USER" >> $SERVICE_FILE
echo "WorkingDirectory=$TCP_SERVER_BRIDGE_DIR" >> $SERVICE_FILE
echo "ExecStart=$TCP_SERVER_BRIDGE_DIR/$TCP_SERVER_BRIDGE_FILE" >> $SERVICE_FILE
echo "SyslogIdentifier=$SYSLOGID" >> $SERVICE_FILE
echo "StandardOutput=syslog" >> $SERVICE_FILE
echo "StandardError=syslog" >> $SERVICE_FILE
echo "Restart=always" >> $SERVICE_FILE
echo "RestartSec=3" >> $SERVICE_FILE
echo "" >> $SERVICE_FILE
echo "[Install]" >> $SERVICE_FILE
echo "WantedBy=multi-user.target" >> $SERVICE_FILE

echo ""
echo "Installation done"
echo ""
echo "enabling and starting the service: systemctl enable $SYSLOGID && systemctl start $SYSLOGID"
systemctl enable $SYSLOGID
systemctl start $SYSLOGID

echo "Service status:"
systemctl status $SYSLOGID


echo "Finish"
