import csv
import requests

### VARIABLES ###
agent_list = []
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents/AGENT_ID"
fleet_agent_url = url + url_endpoint
body = {"tags":["testTag"]}

### SCRIPT ###
agents = requests.put(fleet_agent_url,data=body,auth=("USER","PASS"))
print(agents.json())