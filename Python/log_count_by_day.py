import csv
from elasticsearch import Elasticsearch

index = "INDEX"
date_from = "2022-07-22T00:00:00.000Z"
date_to = "2022-10-26T00:00:00.000Z"
csv_name = "FILE.csv"

es = Elasticsearch(['https://DEPLOYMENT.eastus2.azure.elastic-cloud.com:443'], http_auth=('USER', 'PASS'))
aggregation = es.search(index=index, body={"size":0,"query":{"bool":{"must":[{"match_all":{}}],"filter":[{"range":{"@timestamp":{"gte":date_from,"lte":date_to}}}]}},"aggs":{"log_count_by_day":{"date_histogram":{"field":"@timestamp","calendar_interval":"day"}}}})

with open(csv_name, mode="w") as file:
    writer = csv.writer(file, delimiter=",")
    for result in aggregation["aggregations"]["log_count_by_day"]["buckets"]:
        try:
            date = result["key_as_string"]
        except:
            date = None
        try:
            log_count = result["doc_count"]
        except:
            log_count = None
        
        writer.writerow([date,log_count])
