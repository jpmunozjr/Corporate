# HCR ManorCare, Inc.
# ElasticSearch: Impossible Travel
# Author: Joe Munoz <joseph.munoz@hcr-manorcare.com>
# Last Updated: 1 November 2018
# 
# Queries ElasticSearch for Windows logins, compares locations and alerts if impossible distance conditions are met

import json
import re
import socket
from collections import defaultdict
from elasticsearch import Elasticsearch, helpers
from mysql import connector

#################
### Variables ###
#################

query_conditions = ["Windows-Kerberos_Auth_Ticket_Request", "Windows-Login", "Windows-Successful_Login", "Windows-Successful_Interactive_Login", "Windows-Successful_Service_Login", "Windows-Successful_Remote_Interactive_Login", "Windows-Special_Privilege_New_Logon"]
login_dict = defaultdict(list)

###############
### Program ###
###############

## ElasticSearch ##
es  = Elasticsearch()

for condition in query_conditions:
    response = helpers.scan(client = es,scroll = '5m',index="_all",query={"size":1,"_source":["doc.dstIP","doc.user"],"query":{"bool":{"must":[{"match":{"doc.event1":condition}}],"filter":{"range":{"doc.tOrigin":{"gte":"now-1h","lte":"now"}}}}}})

    for line in response:
        username = str(line['_source']['doc']['user'])
        dstIP = str(line['_source']['doc']['dstIP'][:line['_source']['doc']['dstIP'].rfind(".")])
        
        if login_dict.get(username) == None:
            login_dict[username].append(dstIP)
        elif dstIP in login_dict.get(username):
            pass
        else:
            login_dict[username].append(dstIP)

## MySQL ##

ad_db = connector.connect(
    host="IP_ADDRESS",
    user="foo",
    passwd="foo",
    database="DATABASE"
)

hids_db = connector.connect(
    host="IP_ADDRESS",
    user="USER",
    passwd="PASSWORD",
    database="DATABASE"
)

ad_cursor = ad_db.cursor()
hids_cursor = hids_db.cursor()

for username in login_dict:
    logins = login_dict.get(username)
    if len(logins) > 1:
        for login in logins:
            hids_cursor.execute('SELECT DISTINCT bu,latitude,longitude FROM DATABASE.TABLE WHERE old_corp_subnet_vlan1 LIKE "%' + login + '.%" OR corp_subnet_vlan1 LIKE "%' + login + '.%" OR guest_subnet_vlan5 LIKE "%' + login + '.%" OR voip_subnet_vlan450 LIKE "%' + login + '.%" OR vendor_subnet_vlan7 LIKE "%' + login + '.%" OR wireless_subnet_vlan9 LIKE "%' + login + '.%" OR reserved_subnet LIKE "%' + login + '.%"')
            hids_result = hids_cursor.fetchall()
            
            try:
                bu_login = str(hids_result[0][0])
            except:
                bu_login = "-"
            try:
                lat_login = str(hids_result[0][1])
            except:
                lat_login = "0"
            try:
                lon_login = str(hids_result[0][2])
            except:
                lon_login ="0"
                
            if re.match("^a-", username, re.IGNORECASE):
                ad_cursor.execute('SELECT DISTINCT physicaldeliveryofficename,extensionattribute2 FROM DATABASE.TABLE where samaccountname = "' + username[2:] + '" order by updated desc limit 1')
                ad_result = ad_cursor.fetchall()
            else:
                ad_cursor.execute('SELECT DISTINCT physicaldeliveryofficename,extensionattribute2 FROM DATABASE.TABLE where samaccountname = "' + username + '" order by updated desc limit 1')
                ad_result = ad_cursor.fetchall()
            
            try:
                bu_expected = str(ad_result[0][0])
            except:
                bu_expected = "-"
            try:
                job_code = str(ad_result[0][1])
            except:
                job_code = "-"

            hids_cursor.execute('SELECT DISTINCT latitude,longitude FROM DATABASE.TABLE WHERE bu = "' + bu_expected + '"')
            hids_result = hids_cursor.fetchall()
            
            try:
                lat_expected = str(hids_result[0][0])
            except:
                lat_expected = "0"
            try:
                lon_expected = str(hids_result[0][1])
            except:
                lon_expected = "0"
                
            if bu_expected == "None":
                bu_expected = "-"
            elif job_code == "None":
                job_code = "-"
                
            if bu_expected == "-" or bu_login == "-":
                tags = "Missing BU Information"
            elif bu_expected in bu_login:
                tags = "Match"
            else:
                tags = "Mismatch"

            line = {"username":username,"job_code":job_code,"bu_login":bu_login,"coordinates_login":{"lon":lon_login,"lat":lat_login},"bu_expected":bu_expected,"coordinates_expected":{"lon":lon_expected,"lat":lat_expected},"login":login, "tags":tags}
            
            stream_socket = socket.socket()
            stream_socket.connect(('IP_ADDRESS', 5052))
            stream_socket.sendall(json.dumps(line))
            stream_socket.close()
            
ad_cursor.close()
hids_cursor.close()