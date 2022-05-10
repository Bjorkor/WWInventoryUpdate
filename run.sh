#!/bin/bash

# Author : Zara Ali
# Copyright (c) Tutorialspoint.com
# Script follows here:
curl https://cronitor.link/p/e12853e7180849b99497cbf55f5b8859/1UMI8R?state=run

echo 'pulling source'
activate="/home/ftp/downloads/venv/bin/activate"
source "$activate"
kinit tbarker@hdlusa.lan -k -t '/home/ftp/downloads/tbarker.keytab';
python /home/ftp/downloads/inv.py
if [$? > 0]
then
	https://cronitor.link/p/e12853e7180849b99497cbf55f5b8859/1UMI8R?state=fail
else
	https://cronitor.link/p/e12853e7180849b99497cbf55f5b8859/1UMI8R?state=complete
