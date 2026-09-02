#!/bin/bash
AGENT_IDS=`curl --request GET --url https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents?perPage=5000 --user "USER:PASS" --header "Content-Type: application/json" --header "kbn-xsrf: as" | jq '.list | map(select(.status == "updating")) | map(.agent.id)' | sed 's/\[//g;s/"//g;s/,//g;s/\]//g'`

for ID in $AGENT_IDS
do
	echo $ID
	curl --request POST https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents/$ID/upgrade --user "USER:PASS" --header 'Content-Type: application/json' --header 'kbn-xsrf: as' --data '{"version": "8.8.2","force": true}'
done
