# eDiscovery Device Status
# Author: Joe Munoz
# Last Updated: 23 January 2020
# 
# Automatically starts supervisor, if not already started, when offline devices come online

from mysql import connector
import datetime
import re
import smtplib
import socket
import subprocess
import SERVER_NAME_DATABASE
from elasticsearch import Elasticsearch, helpers
from ssl import create_default_context

#################
### Variables ###
#################

### Lists ###

es_list = []

#################
### Functions ###
#################
	
def peek(query):
    try:
        first = next(query)
    except StopIteration:
        return None
	
###############
### Program ###
###############

print(datetime.datetime.now())

mydb = connector.connect(
	host="IP_ADDRESS",
	user="USER",
	passwd="PASSWORD",
	database="ediscovery"
)

mycursor = mydb.cursor()
mycursor.execute("SELECT name, id FROM DATABASE.TABLE WHERE DATABASE.TABLE.FIELD = 'Running: Looking for Host' AND type = 'equipment' AND name NOT IN (SELECT DISTINCT hostname FROM DATABASE.TABLE)")
query_result = mycursor.fetchall()

for device in query_result:
	hostname = str(device[0]).strip()
	id = str(device[1])
	
	try:
		ip = str(socket.gethostbyname_ex(hostname)[2][0])
	except:
		ip = "-"
	
	if "192." in ip:
		context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
		es = Elasticsearch(
			[{'host': 'SERVER', 'port': 9200}],
			http_auth=('USER', 'PASSWORD'),
			scheme="https",
			port=443,
			ssl_context=context,
		)
		
		es_response = es.search(index="filebeat-*-panw-*",body={"size":1,"query":{"bool":{"must":[{"exists":{"field":"source.ip"}},{"match":{"source.ip":ip}}],"filter":{"range":{"@timestamp":{"gte":"now-1m","lte":"now"}}}}}})
		if es_response['hits']['hits']:
			print("SUCCESS - Firewall - " + hostname + " (" + ip + ") - " + id)
			sql = 'UPDATE `DATABASE`.`TABLE` SET `completed` = NULL, `completedby` = NULL, `collectionstatus` = NULL WHERE `DATABASE`.`TABLE`.`id` = "' + id + '"'
			SERVER_NAME_DATABASE.query(sql)
			subprocess.Popen(['sudo -u ACCOUNT python /path/script.py ' + id], stdout=subprocess.PIPE, shell=True)
		else:
			print("NO RESULTS - Firewall - " + hostname + " (" + ip + ")")
	else:
		context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
		es = Elasticsearch(
			[{'host': 'SERVER', 'port': 9200}],
			http_auth=('USER', 'PASSWORD'),
			scheme="https",
			port=443,
			ssl_context=context,
		)
		
		es_response = es.search(index="packetbeat-*",body={"size":1,"query":{"bool":{"must":[{"match":{"dhcpv4.option.hostname":hostname}}],"filter":{"range":{"@timestamp":{"gte":"now-1m","lte":"now"}}}}}})
		if es_response['hits']['hits']:
			print("SUCCESS - Packetbeat - " + hostname + " (" + ip + ")")
			sql = 'UPDATE `DATABASE`.`TABLE` SET `completed` = NULL, `completedby` = NULL, `collectionstatus` = NULL WHERE `DATABASE`.`TABLE`.`id` = "' + id + '"'
			SERVER_NAME_DATABASE.query(sql)
			subprocess.Popen(['sudo -u ACCOUNT python /path/script.py ' + id], stdout=subprocess.PIPE, shell=True)
		else:
			print("NO RESULTS - Packetbeat - " + hostname + " (" + ip + ")")

print(datetime.datetime.now())