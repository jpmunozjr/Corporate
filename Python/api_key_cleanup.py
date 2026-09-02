from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(
        [{"host":"DEPLOYMENT.eastus2.azure.elastic-cloud.com","scheme":"https","port":443}],
        http_auth=('USER', 'PASS')
)

api_keys = es.search(index="INDEX",body={"size":0,"query":{"bool":{"must":[{"term":{"doc_type":{"value":"api_key"}}},{"term":{"metadata_flattened.managed_by":{"value":"fleet-server"}}}]}},"aggs":{"api_keys":{"terms":{"field":"metadata_flattened.agent_id","size":10000}}}})
for api_key in api_keys["aggregations"]["api_keys"]["buckets"]:
    agent_id = api_key["key"]
    print(agent_id)
    
    agent_id_lookup = es.search(index="INDEX",body={"track_total_hits":"true","size":0,"query":{"bool":{"must":[{"match":{"agent.id":agent_id}}]}}})
    hits_count = agent_id_lookup["hits"]["total"]["value"]
    print(hits_count)
    
    if hits_count == 0:
        print("DELETE")
        es.delete_by_query(index="INDEX",scroll="5m",timeout="5m",body={"query":{"bool":{"must":[{"term":{"doc_type":{"value":"api_key"}}},{"term":{"metadata_flattened.managed_by":{"value":"fleet-server"}}},{"match":{"metadata_flattened.agent_id":agent_id}}]}}})
    else:
        print("ACTIVE AGENT")