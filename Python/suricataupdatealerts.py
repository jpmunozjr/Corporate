import datetime
import os
import requests
import smtplib
import socket

#################
### Functions ###
#################

def kaizalaAlert():
	server = socket.gethostname()
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

	message = "%s:\nSuricata rules are out of date. Please update." % (server)
	message_payload = "{'Message':'" + message + "'}"
	message_response = requests.request("POST", message_url, data=message_payload, headers=message_headers)

#Compare last modified date to current date, send alerts
def lastUpdated():
	#Variables
	currentDate = datetime.datetime.now().date()
	file = '/etc/suricata/rules/sid-msg.map'
	
	try:
		modified = (os.stat(file)).st_mtime
		updateDate = datetime.date.fromtimestamp(modified)
		
		#Out of date files trigger alert switch
		if updateDate != currentDate:
			kaizalaAlert()
		else:
			print("Dates match.")
	except OSError:
		pass

###############
### Program ###
###############

lastUpdated()
