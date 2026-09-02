import csv
from elasticsearch import Elasticsearch

index = "INDEX"
aggregation_name = "hostnames"
csv_name = "FILE.csv"

es = Elasticsearch(['https://DEPLOYMENT.eastus2.azure.elastic-cloud.com:443'], http_auth=('USER', 'PASS'))
aggregation = es.search(index=index, body={"size":0,"query":{"bool":{"must":[{"match_all":{}}],"filter":[{"range":{"@timestamp":{"gte":"now-90d","lte":"now"}}}]}},"aggs":{"hostnames":{"terms":{"field":"observer.hostname","size":10000}}}})

with open(csv_name, mode="w") as file:
    writer = csv.writer(file, delimiter=",")
    for result in aggregation["aggregations"][aggregation_name]["buckets"]:
        try:
            key = result["key"]
        except:
            key = None
        try:
            log_count = result["doc_count"]
        except:
            log_count = None
        
        writer.writerow([key,log_count])
