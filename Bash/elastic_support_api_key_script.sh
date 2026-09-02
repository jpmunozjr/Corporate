ES_HOST="DEPLOYMENT.eastus2.azure.elastic-cloud.com"
ES_PORT="443"
ES_USER="USER"
ES_PASS="PASS"

QUERY=`curl \
  -XPOST \
  "https://$ES_HOST:$ES_PORT/.fleet-agents/_search?filter_path=hits.hits._source.agent.id&q=active:true%20-unenrolled_at:*" \
  -H 'Content-Type: application/json' \
  -u $ES_USER:$ES_PASS \
| jq -c '.hits.hits | map(._source.agent.id) | { query: { bool: { must: [{term: {doc_type: "api_key"}}, {term: {"metadata_flattened.managed_by": "fleet-server"}}], must_not: [{ terms: { "metadata_flattened.agent_id": .} }] }}}'`

echo $QUERY

curl \
  -XPOST \
  "https://$ES_HOST:$ES_PORT/.security/_delete_by_query" \
  -H 'Content-Type: application/json' \
  -u $ES_USER:$ES_PASS \
  -d $QUERY