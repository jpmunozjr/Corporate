import csv
from elasticsearch import Elasticsearch, helpers

index = "logs-*"
csv_name = "tisax_sanand_servers.csv"

es = Elasticsearch(['https://DEPLOYMENT.eastus2.azure.elastic-cloud.com:443'], http_auth=('USER', 'PASS'))
query = helpers.scan(client=es,scroll="5m",index=index,query={"_source":["@timestamp","event.dataset","message"],"query":{"bool":{"must":[{"query_string":{"query":"source.ip:(IP1 OR IP2) OR HOSTNAME"}}],"filter":[{"range":{"@timestamp":{"gte":"now-1h","lte":"now"}}}]}}})

with open(csv_name, mode="w") as file:
    writer = csv.writer(file, delimiter=",")
    for result in query:
        try:
            timestamp = result["_source"]["@timestamp"]
        except:
            timestamp = None
        try:
            dataset = result["_source"]["event"]["dataset"]
        except:
            dataset = None
        try:
            message = result["_source"]["message"]
        except:
            message = None
        
        writer.writerow([timestamp,dataset,message])
