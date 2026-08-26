import csv
import datetime
import HIDSDatabase
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
#
helpDeskList = []
#List of ungrouped source IP addresses and user names
queryResultsItems = []
#List of grouped source IP addresses and user names
queryResultsList = []
#List of unique source IP addresses to ensure no duplicate alerts
srcIPlist = []
#List of logins that will be alerted on
alertList = []

###############
### Program ###
###############

#Queries ElasticSearch with list of admin user names, manipulates data into usable form, and groups user name and source IP into list

#Open list of help desk usernames and append them to list
with open("/path/HelpDeskUserNameList.txt") as file:
	for line in file:
		line = (line.replace('\n', "")).strip()
		helpDeskList.append(line)
		
#Opens list of admin user names
with open("/path/ADUserNameList.txt") as file:
	#Queries each user name
	for line in file:
		#Replaces line breaks and extra space from user name text file for consistency
		line = (line.replace('\n', "")).strip()
		#Query JSON
		esQuery = '{"fields": ["doc.srcIP", "doc.user"], "from": 0, "size": 10000, "query": {"query_string": {"query": "doc.srcIP:[10.0.0.0 TO 10.223.255.255] AND doc.user:' + line + ' AND doc.type:login"}}, "filter":{"bool":{"must":[{"range":{"doc.tOrigin":{"gte":' + str(oneHourAgo) + ',"lte":' + str(currentTime) +',"format":"epoch_millis"}}}]}}}'
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
	#Determines in username is part of help desk groups
	username = queryResult[0]
	#Determines if source IP is already in srcIPlist
	srcIP = queryResult[1]
	#If username is present, do not add help desk member
	if username in helpDeskList:
		pass
	#If srcIP is present, do not add duplicate
	elif srcIP in srcIPlist:
		pass
	#Otherwise, append srcIP to srcIPlist and source IP / user name grouping to alertList
	else:
		srcIPlist.append(srcIP)
		alertList.append(queryResult)

#Enter alertList into HIDS database
for alertItem in alertList:
	alertUser = alertItem[0]
	alertSrc = alertItem[1]
	sql = """INSERT INTO `DATABASE`.`TABLE` (`username`,`sourceip`) VALUES ('%s','%s')""" % (alertUser, alertSrc)
	HIDSDatabase.FUNCTION_NAME(sql)
