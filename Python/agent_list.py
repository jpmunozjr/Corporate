import csv
import requests

### VARIABLES ###
agent_list = []
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents/"
url_modifiers = "?perPage=10000"
fleet_agent_url = url + url_endpoint + url_modifiers

### SCRIPT ###
agents = requests.get(fleet_agent_url,auth=("USER","PASS"))
with open("agent_list.csv", mode="w") as file:
    writer = csv.writer(file, delimiter=",")
    for record in agents.json()["list"]:
        try:
            hostname = record["local_metadata"]["host"]["hostname"]
        except:
            hostname = None
        writer.writerow([hostname])
