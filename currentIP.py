import socket
import smtplib
import time
import os
import subprocess
import getpass

time.sleep(10)

email = "dplaza@tryento.com"
password = "72e(q|{ih2yT"
to = ["rodolfoplaza@hotmail.com", "diegoplazau@hotmail.com"]

hostname = socket.gethostname()
username = getpass.getuser()
local_ip = subprocess.check_output('hostname -I', shell=True)

local_ip = local_ip.decode('ascii')

with smtplib.SMTP_SSL('35.214.219.34', 465) as smtp:

    smtp.login(email, password)

    subject = "{} {}".format(hostname, time.ctime())
    body = " El numero IP para conectarse al usuario <{}> es: \n {}".format(username, local_ip)

    msg = "Subject: {}\n\n{}".format(subject, body)

    smtp.sendmail(email, to, msg)
