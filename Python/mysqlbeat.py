import PRADSDatabase
import subprocess
import sys
from elasticsearch import Elasticsearch, helpers
from mysql import connector
from ssl import create_default_context

rogue_list = []
python_file = '/etc/cron.d/os_fingerprinting.py'

context = create_default_context(cafile="/etc/elasticsearch/certs/ca/ca.pem")
es = Elasticsearch(
	[{'host': 'SERVER', 'port': 9200}],
	http_auth=('USER', 'PASSWORD'),
	scheme="https",
	port=443,
	ssl_context=context,
)

response = helpers.scan(client = es,scroll = '5m',index="mysqlbeat-*",query={"size":1,"_source":["ip_address", "mac_address"],"query":{"bool":{"must":[{"match_all":{}}],"filter":{"range":{"@timestamp":{"gte":"now-2m","lte":"now"}}}}}})

for line in response:
    ip_address = str(line['_source']['ip_address'])
    mac_address = str(line['_source']['mac_address'])
    rogue_list.append([ip_address, mac_address])
    
rogue_list = set(tuple(rogue) for rogue in rogue_list)

prads_db = connector.connect(
    host="IP_ADDRESS",
    user="foo",
    passwd="foo"
    database="DATABASE"
)

prads_cursor = prads_db.cursor()

for rogue in rogue_list:
    ip_address = str(rogue[0])
    mac_address = str(rogue[1])
    
    prads_cursor.execute('SELECT mac_address, ip_address FROM foo.foo WHERE mac_address = "' + mac_address + '" AND DATE_FORMAT(prads.os_fingerprinting.updated, "%Y-%m-%d") <= DATE_SUB(NOW(), INTERVAL 1 DAY)')
    prads_result = prads_cursor.fetchall()
    
    try:
        mac_compare = str(prads_result[0][0])
    except:
        mac_compare = None
        
    if mac_address != mac_compare:
        sql = """REPLACE INTO `foo`.`foo` (`mac_address`,`ip_address`,`hostname`,`device_type`,`operating_system`,`cpe`,`firewall_username`) VALUES ('%s','%s','%s','%s','%s','%s','%s')""" % (mac_address,ip_address, None, None, None, None, None)
        PRADSDatabase.vpuffweb01(sql)
        
        command = 'python ' + python_file + ' -t ' + ip_address + ' -m ' + mac_address + ' &'
        p = subprocess.Popen([str(command)], stdout=subprocess.PIPE, shell=True)
    
prads_cursor.close()
