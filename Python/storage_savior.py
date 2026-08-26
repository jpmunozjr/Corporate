import argparse
import datetime
import paramiko
import re
import requests
import time

#################
### ARG SETUP ###
#################

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", help="hostname of the server to clean up")
args = parser.parse_args()

#################
### VARIABLES ###
#################

hostname = args.server
username = "USER"
password = "PASSWORD"

files = []

#################
### FUNCTIONS ###
#################

def kaizalaAlert(hostname,message):
    application_id = "foo"
    application_secret = "foo"
    refresh_token = "foo"

    token_url = "https://api1.kaiza.la/v1/accessToken"
    token_payload = ""
    token_headers = {
        "applicationId": application_id,
        "applicationSecret": application_secret,
        "refreshToken": refresh_token,
        "cache-control": "no-cache"
    }

    token_response = requests.request("GET", token_url, data=token_payload, headers=token_headers)
    access_token = str(token_response.json()["accessToken"])
    group_id = "foo"
    message_url = "https://api1.kaiza.la/v1/groups/" + group_id + "/messages"
    message_headers = {
        "accessToken": access_token,
        "Content-Type": "application/json",
        "cache-control": "no-cache"
    }

    message = "Storage Savior: %s - %s" % (hostname,message)
    message_payload = "{'Message':'" + message + "'}"
    message_response = requests.request("POST", message_url, data=message_payload, headers=message_headers)

###############
### PROGRAM ###
###############

kaizalaAlert(hostname,"Disk cleanup started.")

try:
    #Get list of large files
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    find_cmd = 'find /var/log -size +1G'
    stdin, stdout, stderr = client.exec_command(find_cmd)

    for line in stdout:
        try:
            line = line.strip('\n')
            files.append(line)
        except:
            pass

    client.close()

    if files == []:
        kaizalaAlert(hostname,"No large files found.")
    else:
        pass
except:
    kaizalaAlert(hostname,"List generation failure. Please check disk manually.")

if files == []:
    pass
else:
    try:
        #Copy files to /path/storage_savior
        for line in files:
            cp_cmd = 'yes | cp -f ' + line + ' /path/storage_savior'
            cp_cmds = ['sudo su',password,cp_cmd]

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=username, password=password)
            channel = client.invoke_shell()

            time.sleep(1) 
            channel.recv(9999)
            channel.send("\n")
            time.sleep(1)

            for command in cp_cmds:
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(1)
                time.sleep(1)

        channel.close()

    except:
        kaizalaAlert(hostname,"File copy failure. Please check disk manually.")

    try:
        #Clear data from files to free disk space
        for line in files:
            clear_cmd = 'echo " " > ' + line
            clear_cmds = ['sudo su',password,clear_cmd]

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=username, password=password)
            channel = client.invoke_shell()

            time.sleep(1)
            channel.recv(9999)
            channel.send("\n")
            time.sleep(1)

            for command in clear_cmds:
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(1)
                time.sleep(1)

        channel.close()

        kaizalaAlert(hostname,"Disk cleanup finished.")
    except:
        kaizalaAlert(hostname,"Disk cleanup failed. Please check disk manually.")

exit()
