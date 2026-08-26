import csv
import datetime
from elasticsearch import Elasticsearch, helpers
from ssl import create_default_context

todays_date = str(datetime.datetime.now().date())
csv_name = '/path/Reports/' + todays_date + '-url_usernames.csv'
final_list = []

context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
es = Elasticsearch(
        [{'host': 'SERVER', 'port': 9200}],
        http_auth=('USER', 'PASSWORD'),
        scheme="https",
        port=443,
        ssl_context=context,
		timeout=10000,
)

url_ips = helpers.scan(client=es,scroll='5m',index="filebeat-*-panw-*",query={"_source":["source.ip"],"query":{"bool":{"must":[{"wildcard":{"url.original":{"value":"firebasestorage.googleapis.com*"}}}],"filter":{"range":{"@timestamp":{"gte":"now-7d","lte":"now"}}}}}})
for line in url_ips:
	source_ip = None
	username = None
	source_ip = str(line["_source"]["source"]["ip"])
	
	url_usernames = helpers.scan(client=es,scroll='5m',index="asset_list-*",query={"_source":["user.name"],"size":1,"query":{"bool":{"must":[{"match":{"source.ip":source_ip}}],"filter":{"range":{"@timestamp":{"gte":"now-7d","lte":"now"}}}}}})
	for line in url_usernames:
		username = str(line["_source"]["user.name"])
		
	final_list.append([source_ip,username])

final_list = set(tuple(result) for result in final_list)

with open(csv_name, mode='w') as file:
	writer = csv.writer(file, delimiter=',')
	writer.writerow(["source_ip","username"])
	writer.writerows(final_list)