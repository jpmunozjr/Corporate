import argparse
import json
import os
import PRADSDatabase
import re
import socket
import subprocess
from elasticsearch import Elasticsearch, helpers
from ssl import create_default_context

#################
### Variables ###
#################

#Target argument
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--target", default=None, help="target ip")
parser.add_argument("-m", "--mac", default=None, help="target mac address")
args = parser.parse_args()

ip_address = str(args.target)
mac_address = str(args.mac)
nmap_filename = "/tmp/nmap-" + ip_address
hostname = None
operating_system = None
device_type = None
cpe = None
tags = None

print(ip_address, mac_address)

#################
### Functions ###
#################

def send_to_elk(log):
	stream_socket = socket.socket()
	stream_socket.connect(('IP_ADDRESS', 5054))
	stream_socket.sendall(json.dumps(log))
	stream_socket.close()

def variable_regex(string, regex_string,split_variable,select_variable):
	variable = None
	try:
		#variable = re.search(regex_string, string, re.IGNORECASE).group(0)
		variable = (((re.search(regex_string, string, re.IGNORECASE).group()).split(split_variable))[select_variable]).lower()
	except:
		pass
	return variable
		
###############
### Program ###
###############

context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
es = Elasticsearch(
	[{'host': 'SERVER', 'port': 9200}],
	http_auth=('USER', 'PASSWORD'),
	scheme="https",
	port=443,
	ssl_context=context,
)

firewall_response = es.search(index="filebeat-*-panw-*",body={"size": 1,"_source": ["source.user.name"],"query": {"bool": {"must": [{"match": {"source.ip": ip_address}}],"filter": {"range": {"@timestamp": {"gte": "now-1h","lte": "now"}}}}}},filter_path=['hits.hits._source'])

if firewall_response == {}:
	username = None
else:
	username = firewall_response['hits']['hits'][0]['_source']['source']['user']['name']

#NMAP scan into a file
command = 'nmap -sV -sC ' + args.target + ' > ' + nmap_filename
p = subprocess.Popen([str(command)], stdout=subprocess.PIPE, shell=True)
p.communicate()

with open(nmap_filename, 'r') as file:
	content_full = file.read()
with open(nmap_filename, 'r') as file:
	content_array = file.readlines()
	
if "Host seems down." in content_full:
	tags = "host_offline"
	json_line = {"source_ip":ip_address,"tags":tags}
	send_to_elk(json_line)
elif "Too many fingerprints match this host" in content_full:
	tags = "ambiguous_fingerprint"
	json_line = {"source_ip":ip_address,"tags":tags}
	send_to_elk(json_line)
	
while hostname == None:
	hostname = variable_regex(content_full, 'Computer name: [A-Za-z0-9]*', 'name: ', 1)
	
	if hostname != None:
		break
	
	hostname = variable_regex(content_full, 'Nmap scan report (?!for [0-9]*[.][0-9]*[.][0-9]*[.][0-9]*)for [^.]*', 'for ', 1)
	
	if hostname != None:
		break
	
	hostname = variable_regex(content_full, 'Service Info: Host: [^;]*', 'Host: ', 1)
	
	if hostname != None:
		break
	else:
		break
	
while operating_system == None:
	operating_system = variable_regex(content_full, '\|   OS: [A-Za-z0-9 ]*[(][^)]*[)]', 'OS: ', 1)
	
	if operating_system != None:
		break
	else:	
		break

for line in content_array:
	if "Service Info" in line:
		while operating_system == None:
			operating_system = variable_regex(line, 'OS: [^;]*', 'OS: ', 1)
			
			if operating_system != None:
				break
				
			operating_system = variable_regex(line, 'OSs: [^;]*', 'OSs: ', 1)
			
			if operating_system != None:
				break
			else:
				break

		while device_type == None:
			device_type = variable_regex(line, 'Device: [^;]*', 'Device: ', 1)

			if device_type != None:
				break
			else:
				break

		while cpe == None:
			cpe = variable_regex(line, 'CPE: [A-Za-z0-9:/]*', 'CPE: ', 1)
			
			if cpe != None:
				break
			else:
				break
if tags == "host_offline" or tags == "ambiguous_fingerprint":
	sql = """REPLACE INTO `DATABASE`.`TABLE` (`mac_address`,`ip_address`,`hostname`,`device_type`,`operating_system`,`cpe`,`firewall_username`) VALUES ('%s','%s','%s','%s','%s','%s','%s')""" % (mac_address,ip_address,None,None,None,None,username)
	PRADSDatabase.FUNCTION_NAME(sql)
else:
	json_line = {"source_ip":ip_address,"hostname":hostname,"operating_system":operating_system,"device_type":device_type,"cpe":cpe}
	send_to_elk(json_line)
	
	#Write to PRADS table
	sql = """REPLACE INTO `DATABASE`.`TABLE` (`mac_address`,`ip_address`,`hostname`,`device_type`,`operating_system`,`cpe`,`firewall_username`) VALUES ('%s','%s','%s','%s','%s','%s','%s')""" % (mac_address,ip_address,hostname,device_type,operating_system,cpe,username)
	PRADSDatabase.FUNCTION_NAME(sql)

#Delete tmp nmap scan file
os.remove(nmap_filename)
