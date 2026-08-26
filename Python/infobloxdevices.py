# PRADS Seen Devices Process
# Author: Joe Munoz
# Last Updated: 18 September 2018
# 
# Inserts seen devices into PRADS database to help to find rogues

import datetime
import PRADSDatabase
import re
from elasticsearch import Elasticsearch, helpers

###############
### Program ###
###############

print(datetime.datetime.now())

#Start ElasticSearch client
es = Elasticsearch()
#Query Infoblox index with scroll
es_response = helpers.scan(client = es,scroll = '5m',index="infoblox-*",query={"size":1,"_source":["infoblox_mac","infoblox_ip","infoblox_hostname"],"query":{"bool":{"must":[{"exists":{"field":"infoblox_ip"}}],"filter":{"range":{"@timestamp":{"gte":"now-1m","lte":"now"}}}}}})

#Loop through ElasticSearch response
for line in es_response:
	#Select _source line, returns mac, ip, and hostname
	result = str(line['_source']).strip()

	#Remove unnecessary characters from line
	for change in ["{", "}", "u'", "'"]:
		if change in result:
			result = result.replace(change, "")
	
	insert = None
	
	#Parse lines with a hostname
	if "hostname" in result:
		#Parse hostname
		try:
			hostname = ((re.search('infoblox_hostname: [^,]*', result, re.IGNORECASE)).group(0)).split(" ")[-1]
		except:
			pass
		#Parse IP address
		try:
			ip = ((re.search('infoblox_ip: [^,]*', result, re.IGNORECASE)).group(0)).split(" ")[-1]
		except:
			pass
		#Parse MAC address
		try:
			mac = (((re.search('infoblox_mac: .*', result, re.IGNORECASE)).group(0)).split(" ")[-1]).replace(":", "")
		except:
			insert = False

		#Do not insert into database without MAC address
		if insert == 'False':
			continue
		#Insert into database
		else:
			sql = """REPLACE INTO `DATABASE`.`TABLE` (`hostname`,`ip_address`,`mac_address`) VALUES ('%s','%s','%s')""" % (hostname, ip, mac)
			PRADSDatabase.FUNCTION_NAME(sql)
			
	#Parse lines without a hostname
	else:
		#Parse IP address
		try:
			ip = ((re.search('infoblox_ip: [^,]*', result, re.IGNORECASE)).group(0)).split(" ")[-1]
		except:
			pass
		try:
			hostname = (socket.gethostbyaddr(ip))[0]
		except:
			pass
		#Parse MAC address
		try:
			mac = (((re.search('infoblox_mac: .*', result, re.IGNORECASE)).group(0)).split(" ")[-1]).replace(":", "")
		except:
			insert = False
			
		#Do not insert into database without MAC address
		if insert == 'False':
			continue
		elif hostname:
			sql = """REPLACE INTO `DATABASE`.`TABLE` (`hostname`,`ip_address`,`mac_address`) VALUES ('%s','%s','%s')""" % (hostname, ip, mac)
			PRADSDatabase.FUNCTION_NAME(sql) 
		#Insert into database
		else:
			sql = """REPLACE INTO `DATABASE`.`TABLE` (`ip_address`,`mac_address`) VALUES ('%s','%s')""" % (ip, mac)
			PRADSDatabase.FUNCTION_NAME(sql)
		
print(datetime.datetime.now())
print("--------------------------")