import csv
import requests

### VARIABLES ###
agent_list = []
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
agent_endpoint = "api/fleet/agents/"
agent_modifiers = "?perPage=10000"
fleet_agent_url = url + agent_endpoint + agent_modifiers
policy_endpoint = "api/fleet/agent_policies/"
fleet_policy_url = url + policy_endpoint

### SCRIPT ###
agents = requests.get(fleet_agent_url,auth=("USER","PASS"))
with open("FILE.csv", mode="w") as file:
    writer = csv.writer(file, delimiter=",")
    for agent in agents.json()["list"]:
        try:
            hostname = agent["local_metadata"]["host"]["hostname"]
        except:
            hostname = None
        try:
            enrollment_time = agent["enrolled_at"]
        except:
            enrollment_time = None
        try:
            policy_id = agent["policy_id"]
        except:
            policy_id = None

        fleet_policy_url = url + policy_endpoint
        fleet_policy_url = fleet_policy_url + policy_id
        policies = requests.get(fleet_policy_url,auth=("USER","PASS"))
        
        try:
            policy_name = policies.json()["item"]["name"]
        except:
            policy_name = None

        writer.writerow([hostname,enrollment_time,policy_id,policy_name])
