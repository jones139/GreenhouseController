System Scripts for Greenhouse Controller
########################################


Copy systemd/system/greenhouse.service to /lib/systemd/system
chmod 644 /lib/systemd/system/greenhouse.service
chmod +x /home/graham/GreenhouseController/greenhouseServer/greenhouseSvr.py

systemctl daemon-reload
systemctl enable greenhouse.service
systemctl start greenhouse.service

journalctl -f -u greenhouse.service (view log)