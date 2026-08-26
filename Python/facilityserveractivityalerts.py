import csv
import datetime
import HIDSDatabase
import socket
import time
import urllib2

#################
### Variables ###
#################

#ElasticSearch API URL with results filter to only return hits
url = 'http://localhost:9200/_search?pretty&filter_path=hits.hits.fields'
#Produces current time in milliseconds
currentTime = int(int(time.time())*1000)
#Produces current time in milliseconds minus one hour
oneHourAgo = currentTime - 3600000
#Produces current date to add on to CSV file
date = datetime.datetime.now()
#Produces current hour to add on to CSV file
hour = (datetime.datetime.now()).hour
#List of ungrouped source and destination IP addresses
queryResultsItems = []
#List of grouped source and destination IP addresses
queryResultsList = []
#List of source IP addresses for use in zip
srcIPlist = []
#List of destination IP addresses for use in zip
dstIPlist = []
#List of host names for use in zip
hostnameList = []
#List of source IP addresses, destination IP addresses, and host names
zippedList = []
#List of unique source IP addresses to ensure no duplicate alerts
duplicateList = []
#List of logins that will be alerted on
alertList = []

###############
### Program ###
###############

#Queries ElasticSearch with list of server IP addresses, manipulates data into usable form, and groups source IP, destination IP, host name, and date into list

#Opens list of server IP addresses
with open("/mnt/reports/LCE_Queries/ServerIPAddressList.txt") as file:
	#Queries each IP address
	for line in file:
		#Replaces line breaks and extra space from IP address text file for consistency
		line = (line.replace('\n', "")).strip()
		#Query JSON
		esQuery = '{"fields": ["doc.srcIP", "doc.dstIP"], "from": 0, "size": 10000, "query": {"query_string": {"query": "doc.srcIP:[10.0.0.0 TO 10.223.255.255] AND doc.dstIP:' + line +'"}}, "filter":{"bool":{"must":[{"range":{"doc.tOrigin":{"gte":' + str(oneHourAgo) + ',"lte":' + str(currentTime) +',"format":"epoch_millis"}}}]}}}'
		#HTTP POST request and response
		postRequest = urllib2.Request(url, esQuery)
		queryResults = urllib2.urlopen(postRequest)

		#Cycles through the query response
		for queryResult in queryResults:
			#Focuses on usable data, the data separated by :
			if ":" in queryResult:
				#Replaces line breaks, commas, quotations, brackets, etc. from query data
				for change in ["\n", '"', "'", ",", "[", "]", " ", "{", "}"]:
					if change in queryResult:
						queryResult = ((queryResult.split(":")[-1]).replace(change, "")).strip()
				#Skips blank data left by replacing characters
				if queryResult == '':
					pass
				#Appends usable data to queryResultsItems
				else:
					queryResultsItems.append(queryResult)

#Groups data items by 2 (user name and source IP) into queryResultsList
for queryResultItem in range(0, len(queryResultsItems), 2):
	queryResultsList.append(queryResultsItems[queryResultItem : queryResultItem+2])

#Cycles through queryResultsList
for queryResult in queryResultsList:
	#Designate source IP, destination IP, and host names
	srcIP = queryResult[0]
	dstIP = queryResult[1]
	hostname = (socket.gethostbyaddr(dstIP)[0])
	#Append source IP, destination IP, and host name into lists
	srcIPlist.append(srcIP)
	dstIPlist.append(dstIP)
	hostnameList.append(hostname)

zippedList = zip(srcIPlist, dstIPlist, hostnameList)

#Cycles through zippedList	
for zipResult in zippedList:
	#Determine if source and destination are the same, or if source IP is already present
	duplicateSrcIP = zipResult[0]
	duplicateDstIP = zipResult[1]
	#If source and destination the same, do not add to alerts
	if duplicateSrcIP == duplicateDstIP:
		pass
	#If srcIP is present, do not add duplicate
	if duplicateSrcIP in duplicateList:
		pass
	#Otherwise, append srcIP to srcIPlist and source IP / user name grouping to alertList
	else:
		duplicateList.append(duplicateSrcIP)
		alertList.append(zipResult)

#Enter alertList into HIDS database
for alertItem in alertList:
	alertSrc = alertItem[0]
	alertDst = alertItem[1]
	alertHost = alertItem[2]
	sql = """INSERT INTO `DATABASE`.`TABLE` (`sourceip`,`destinationip`,`hostname`) VALUES ('%s','%s','%s')""" % (alertSrc, alertDst, alertHost)
	HIDSDatabase.FUNCTION_NAME(sql)
