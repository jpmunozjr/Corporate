import csv
import json
from elasticsearch import Elasticsearch

index = "logs-*"
composite_aggregation_name = "agg_scroll"
date_histogram_name = "logs_per_day"
terms_aggregation_name = "dataset_count"
gte = "now-1h"
lte = "now"

es = Elasticsearch(['https://DEPLOYMENT.eastus2.azure.elastic-cloud.com:443'], http_auth=('USER', 'PASS'))
aggregation = es.search(index=index,request_timeout=300,body={"size":0,"query":{"bool":{"filter":[{"range":{"@timestamp":{"gte":gte,"lte":lte}}}]}},"aggs":{composite_aggregation_name:{"composite":{"sources":[{date_histogram_name:{"date_histogram":{"field":"@timestamp","calendar_interval":"day"}}}]},"aggs":{terms_aggregation_name:{"terms":{"field":"event.dataset","size":100}}}}}})

time_payload = aggregation["aggregations"][composite_aggregation_name]["buckets"]
for time in time_payload:
    try:
        timestamp = time["key"][date_histogram_name]
    except:
        timestamp = None

    for count in time[terms_aggregation_name]["buckets"]:
        try:
            dataset_name = count["key"]
        except:
            dataset_name = None
        try:
            dataset_count = count["doc_count"]
        except:
            dataset_count = None

        json_body = json.dumps({"@timestamp":timestamp,"dataset.name":dataset_name,"dataset.count":dataset_count})
        print(json_body)
