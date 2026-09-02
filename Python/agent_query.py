import csv
import requests

### VARIABLES ###
agent_list = []
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents"
url_query = "?kuery=local_metadata.host.hostname%3A%22AGENT_NAME%22"
fleet_agent_url = url + url_endpoint + url_query

### SCRIPT ###
agents = requests.get(fleet_agent_url,auth=("USER","PASS"))
for record in agents.json()["list"]:
    agent_name = record["local_metadata"]["host"]["hostname"]
    agent_status = record["status"]
    agent_id = record["id"]
    print(agent_name,agent_id,agent_status)
