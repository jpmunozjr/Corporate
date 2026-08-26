import csv
import datetime
import socket
import PRADSDatabase
from elasticsearch import Elasticsearch, helpers
from mysql import connector
from ssl import create_default_context

print(datetime.datetime.now())

#################
### VARIABLES ###
#################

result_list = []
current_date = str(datetime.datetime.today().strftime('%Y-%m-%d'))
header = ["USERNAME", "NAME", "TITLE", "JOB CODE", "BUSINESS UNIT", "SOURCE IP", "SOURCE MACHINE", "DESTINATION IP", "DESTINATION MACHINE", "REDIRECT URL", "COUNT", "REFERER URL", "ACTION"]

username_counter = 0
source_ip_counter = 0
to_url_counter = 0
from_url_counter = 0
destination_ip_counter = 0

#Elasticsearch connection
context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
es = Elasticsearch(
        [{'host': 'SERVER', 'port': 9200}],
        http_auth=('USER', 'PASSWORD'),
        scheme="https",
        port=443,
        ssl_context=context,
        timeout=10000,
)

#Parse username
query1 = es.search(index="filebeat-*-panw-*",body={"size":0,"query":{"bool":{"must":[{"exists":{"field":"source.user.name"}}],"filter":{"range":{"@timestamp":{"gte":"now-1d","lte":"now"}}}}},"aggs":{"top_100_users":{"terms":{"field":"source.user.name.keyword","size":100},"aggs":{"all_source_ips":{"terms":{"field":"source.ip.keyword","size":20},"aggs":{"to_url":{"terms":{"field":"url.original.keyword","size":20},"aggs":{"from_url":{"terms":{"field":"http.request.referer.keyword","size":1},"aggs":{"destination_ip":{"terms":{"field":"destination.ip.keyword","size":1},"aggs":{"action":{"terms":{"field":"event.outcome.keyword","size":1}}}}}}}}}}}}}})
for line in query1['aggregations']['top_100_users']['buckets']:
    username = str(line['key_as_string']).split('\\')[1]
    
    #MySQL connection
    ad_db = connector.connect(
        host="IP_ADDRESS",
        user="USER",
        passwd="PASSWORD",
        database="DATABASE"
    )
    ad_cursor = ad_db.cursor()

    #Job code and business unit query
    ad_cursor.execute('SELECT physicaldeliveryofficename,extensionattribute2,title,displayname FROM DATABASE.TABLE WHERE cn = "' + username + '"')
    ad_result = ad_cursor.fetchall()
    
    try:
        business_unit = str(ad_result[0][0])
    except:
        business_unit = None
    try:
        job_code = str(ad_result[0][1])
    except:
        job_code = None
    try:
        title = str(ad_result[0][2])
    except:
        title = None
    try:
        name = str(ad_result[0][3])
    except:
        name = None
        
    ad_cursor.close()
    
    try:
        #Parse source IP
        for line in query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets']:
            source_ip = str(line['key'])

            #Resolve source IP
            try:
                source_machine = socket.gethostbyaddr(source_ip)[0]
            except:
                source_machine = None
            
            #Records without URLs
            if query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets'] == []:
            
                to_url = None
                from_url = None
                
                #Parse destination IP and count
                query2 = es.search(index="filebeat-*-panw-*",body={"size":0,"query":{"bool":{"must":[{"match":{"source.user.name":username}},{"match":{"source.ip":source_ip}}],"filter":{"range":{"@timestamp":{"gte":"now-1d","lte":"now"}}}}},"aggs":{"destination_ip":{"terms":{"field":"destination.ip.keyword","size":20},"aggs":{"action":{"terms":{"field":"event.outcome.keyword","size":1}}}}}})
                for line in query2['aggregations']['destination_ip']['buckets']:
                    destination_ip = str(line['key'])
                    count = str(line['doc_count'])

                    #Resolve destination IP
                    try:
                        destination_machine = socket.gethostbyaddr(destination_ip)[0]
                    except:
                        destination_machine = None

                    #Parse action
                    for line in query2['aggregations']['destination_ip']['buckets'][destination_ip_counter]['action']['buckets']:
                        action = str(line['key'])
                        
                        #Collect results for CSV
                        result_list.append(list([username,name,title,job_code,business_unit,source_ip,source_machine,destination_ip,destination_machine,to_url,count,from_url,action]))
                        
                    #Counter to help select correct data per destination IP
                    if destination_ip_counter == 19:
                        destination_ip_counter = 0
                    else:
                        destination_ip_counter = destination_ip_counter + 1
            else:
                #Parse URL and count
                for line in query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets']:
                    to_url = str(line['key'])
                    count = str(line['doc_count'])
                    
                    if query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets'][to_url_counter]['from_url']['buckets'] == []:
                        from_url = None

                        query3 = es.search(index="filebeat-*-panw-*",body={"size":0,"query":{"bool":{"must":[{"match":{"source.user.name":username}},{"match":{"source.ip":source_ip}},{"match":{"url.original":to_url}}],"filter":{"range":{"@timestamp":{"gte":"now-1d","lte":"now"}}}}},"aggs":{"destination_ip":{"terms":{"field":"destination.ip.keyword","size":1},"aggs":{"action":{"terms":{"field":"event.outcome.keyword","size":1}}}}}})
                        for line in query3['aggregations']['destination_ip']['buckets']:
                            destination_ip = str(line['key'])
                            count = str(line['doc_count'])

                            #Resolve destination IP
                            try:
                                destination_machine = socket.gethostbyaddr(destination_ip)[0]
                            except:
                                destination_machine = None

                            for line in query3['aggregations']['destination_ip']['buckets'][0]['action']['buckets']:
                                action = str(line['key'])

                                #Collect results for CSV
                                result_list.append(list([username,name,title,job_code,business_unit,source_ip,source_machine,destination_ip,destination_machine,to_url,count,from_url,action]))
                    else:
                        #Parse URL and count
                        for line in query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets'][to_url_counter]['from_url']['buckets']:
                            from_url = str(line['key'])
                            
                            for line in query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets'][to_url_counter]['from_url']['buckets'][0]['destination_ip']['buckets']:
                                destination_ip = str(line['key'])
                                
                                #Resolve destination IP
                                try:
                                    destination_machine = socket.gethostbyaddr(destination_ip)[0]
                                except:
                                    destination_machine = None
                                    
                                for line in query1['aggregations']['top_100_users']['buckets'][username_counter]['all_source_ips']['buckets'][source_ip_counter]['to_url']['buckets'][to_url_counter]['from_url']['buckets'][0]['destination_ip']['buckets'][0]['action']['buckets']:
                                    action = str(line['key'])
                                    
                                    #Collect results for CSV
                                    result_list.append(list([username,name,title,job_code,business_unit,source_ip,source_machine,destination_ip,destination_machine,to_url,count,from_url,action]))
for line in result_list:
	print(line)