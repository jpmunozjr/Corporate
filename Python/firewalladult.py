import datetime
import PRADSDatabase
import socket
import urllib2
from elasticsearch import Elasticsearch, helpers
from ssl import create_default_context

sql_list = []

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
		timeout=10000,
)
es_response = helpers.scan(client = es,scroll = '5m',index="filebeat-*-panw-*",query={"_source": ["@timestamp", "source.ip", "destination.ip","url.original","panw.panos.url.category", "panw.panos.ruleset", "source.user.name", "network.application", "event.outcome"],"query": {"bool": {"must": [{"exists": {"field": "source.ip"}},{"match": {"panw.panos.url.category": "adult"}},{"match":{"event.outcome": "block-url"}}],"filter": {"range":{"@timestamp":{"gte": "now-1d","lte": "now"}}}}}})
for line in es_response:
	date = str(line['_source']['@timestamp'])
	source_ip = str(line['_source']['source']['ip'])
	destination_ip = str(line['_source']['destination']['ip'])
	application = str(line['_source']['network']['application'])
	webfiltering_category = str(line['_source']['panw']['panos']['ruleset'])
	action = str(line['_source']['event']['outcome'])
	web_category = str(line['_source']['panw']['panos']['url']['category'])
	try:
		url = str(line['_source']['url']['original'])
	except:
		url = None
	try:
		username = str(line['_source']['source']['user']['name']).split('\\')[1]
	except:
		username = None

	sql = """INSERT INTO `DATABASE`.`TABLE` (date,username,source_ip,destination_ip,application,url,action,web_category,webfiltering_category) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (date,username,source_ip,destination_ip,application,url,action,web_category,webfiltering_category)
	PRADSDatabase.FUNCTION_NAME(sql)