import os
import smtplib
import socket
import subprocess
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mount_file = "/proc/mounts"
mount_path = "/mnt"
mount_command = "mount -a"

not_mounted = []
mount_failures = []

def email_alert(server, html):
    mailFrom = "EMAIL"
    mailTo = "EMAIL"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s - Mount Failure" % (server)
    msg['From'] = mailFrom
    msg['To'] = mailTo
    attachment = MIMEText(html, 'html')
    msg.attach(attachment)
    s = smtplib.SMTP("MAIL_SERVER")
    s.sendmail(mailFrom, mailTo, msg.as_string())
    s.quit()

#First check
with open(mount_file, 'r') as file:
    content = file.read()
    
for mount in os.listdir(mount_path):
    if mount in content:
        print(mount + " is mounted.")
        pass
    else:
        print(mount + " not mounted. Attempting to remount.")
        not_mounted.append(mount)
        subprocess.Popen([mount_command], stdout=subprocess.PIPE, shell=True)

time.sleep(10)
        
#Second check
with open(mount_file, 'r') as file:
    content = file.read()
    
for mount in os.listdir(mount_path):
    if mount in content:
        print(mount + " is mounted.")
        pass
    else:
        print(mount + " not mounted. Sending email alert.")
        mount_failures.append(mount)

if mount_failures:
	server = socket.gethostname()
	items = ["\n    <li>{}</li>".format(failure) for failure in mount_failures]
	items = "".join(items)
	html = '<html><head></head><body>The following mounts on %s are not active, and could not be automatically corrected:<br>%s<br><br>Please investigate.</body></html>' % (server, items)
	email_alert(server, html)