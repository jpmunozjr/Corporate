from __future__ import division
import csv
import datetime
import subprocess
from elasticsearch import Elasticsearch, helpers
from mysql import connector
from ssl import create_default_context

total_list = 0
complete = 0
count = 0
sum = 0

total_pct = []
complete_list = []
incomplete_list = []

total_servers = 758

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

with open('/path/server_bundle_list.txt', 'r') as file:
    for line in file:
        if "#" in line:
            pass
        else:
            total_list = total_list + 1
            
            hostname = line.strip()
            query = es.search(index="winlogbeat-*",body={"size":0,"track_total_hits": 10000000,"query":{"bool":{"must":[{"match":{"agent.hostname":hostname}}],"filter":{"range":{"@timestamp":{"gte":"now-24h","lte":"now"}}}}}})
            past_day_hits = query['hits']['total']['value']
            
            if past_day_hits == 0:
                status = "incomplete"
                incomplete_list.append([hostname, past_day_hits, status])
            else:
                status = "complete"
                complete = complete + 1
                complete_list.append([hostname, past_day_hits, status])

attempt_percentage = (total_list / total_servers) * 100
complete_percentage = (complete / total_servers) * 100
incomplete_percentage = ((total_servers - complete) / total_servers) * 100

response = subprocess.Popen(['curl','-s','-k','https://SERVER:9200/_cat/allocation?v&s=node&h=node,disk.used,disk.percent'], stdout=subprocess.PIPE)
output, error = response.communicate()
output = output.split("\n")

for line in output[1:]:
    if line == '':
        pass
    else:
        count = count + 1
        line = (' '.join(line.split())).split(" ")
        
        node = line[0]
        used_size = line[1]
        used_pct = line[2]
        total_pct.append(used_pct)

for line in total_pct:
    sum = sum + int(line)
    
total_pct = sum / count

csv_name = "/path/server-bundle-progress_" + str(datetime.date.today()) + ".csv"
with open(csv_name, mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Hostname","Log Count - Past 24 Hours","Status"])
    
    for line in complete_list:
        writer.writerow(line)
    for line in incomplete_list:
        writer.writerow(line)

    writer.writerow(["-","-","-"])
    writer.writerow(["Attempt %","Complete %","Incomplete %"])
    writer.writerow([attempt_percentage,complete_percentage,incomplete_percentage])
    
    writer.writerow(["-"])
    writer.writerow(["% Disk Used"])
    writer.writerow([total_pct])