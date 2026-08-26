import datetime
import socket
import PRADSDatabase
from elasticsearch import Elasticsearch, helpers
from mysql import connector
from ssl import create_default_context

username_counter = 0

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

alf_query = es.search(index="admin_login_failures-*",body={"size":0,"query":{"bool":{"must_not":[{"wildcard":{"job_code.keyword":"VIS*"}}],"filter":{"range":{"@timestamp":{"gte":"now-1d","lte":"now"}}}}},"aggs":{"top_usernames":{"terms":{"field":"username.keyword"},"aggs":{"top_event":{"terms":{"field":"event1.keyword","size":1},"aggs":{"timestamp":{"terms":{"field":"@timestamp","size":1000}}}}}}}})
for line in alf_query['aggregations']['top_usernames']['buckets']:
	username = str(line['key'])
	
	#MySQL connection
	ad_db = connector.connect(
		host="IP_ADDRESS",
		user="ACCOUNT",
		passwd="PASSWORD",
		database="activedirectory"
	)
	ad_cursor = ad_db.cursor()

	#Job code and business unit query
	ad_cursor.execute('SELECT physicaldeliveryofficename,extensionattribute2,title,displayname FROM DATABASE_NAME WHERE cn = "' + username + '"')
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
	
	for line in alf_query['aggregations']['top_usernames']['buckets'][username_counter]['top_event']['buckets']:
		event = str(line['key'])
		count = str(line['doc_count'])
		
		for line in alf_query['aggregations']['top_usernames']['buckets'][username_counter]['top_event']['buckets'][0]['timestamp']['buckets']:
			timestamp = str(line['key'])

			#print(timestamp,username,business_unit,job_code,title,name,event,count)
			sql = """INSERT INTO `DATABASE_NAME`.`TABLE_NAME` (date,username,business_unit,job_code,title,name,event,count) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')""" % (timestamp,username,business_unit,job_code,title,name,event,count)
			PRADSDatabase.FUNCTION_NAME(sql)

	username_counter = username_counter + 1