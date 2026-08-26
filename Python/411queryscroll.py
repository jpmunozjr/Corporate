# ElasticSearch: Windows Event Query
# Author: Joe Munoz
# Last Updated: 18 September 2018
# 
# Queries ElasticSearch for Windows event 411, failed ADFS validations

import csv
import datetime
import HIDSDatabase
import re
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
#List of grouped source IP addresses and user names
queryResultsList = []

###############
### Program ###
###############

#Query JSON
esQuery = '{"fields": ["doc.rawLog"], "from": 0, "size": 10000, "query": {"query_string": {"query": "doc.event1:Windows-ADFS_Token_Validation_Failed AND doc.rawLog:411"}}}'
#HTTP POST request and response
postRequest = urllib2.Request(url, esQuery)
queryResults = urllib2.urlopen(postRequest)

#Cycles through the query response
for queryResult in queryResults:
        username = re.search('[^\s]*@DOMAIN', queryResult, re.IGNORECASE)
        ipaddress = re.search('Client IP: [^\s]*', queryResult)
        if username and ipaddress:
                #Parse out useful data
				username = username.group(0)
                ipaddress = ipaddress.group(0)
                ipaddress = ipaddress.split(" ")[2]
                try:
                        ip1 = ipaddress.split(",")[0]
                        ip2 = ipaddress.split(",")[1]
                except:
                        pass
                #Add data to list
				queryResultsList.append(list([username, ip1, ip2]))
#Save to csv
with open(r'/path/adfs_411_usernames_ipaddresses.csv', 'wb') as file:
        writer = csv.writer(file, delimiter=",")
        for line in queryResultsList:
                writer.writerows([line])