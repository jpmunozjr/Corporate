import requests

### VARIABLES ###
offline_count = 0
agent_dictionary = {}
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents"
url_modifiers = "?perPage=10000"
fleet_agent_url = url + url_endpoint + url_modifiers

### FUNCTIONS ###
def append_value(dict_obj, key, value):
    if key in dict_obj:
        if not isinstance(dict_obj[key], list):
            dict_obj[key] = [dict_obj[key]]
        dict_obj[key].append(value)
    else:
        dict_obj[key] = value

### SCRIPT ###
agents = requests.get(fleet_agent_url,auth=("USER","PASS"))
for record in agents.json()["list"]:
    try:
        id = record["id"]
    except:
        id = None
    try:
        hostname = record["local_metadata"]["host"]["hostname"]
    except:
        hostname = None
    try:
        status = record["status"]
    except:
        status = None
    
    append_value(agent_dictionary, hostname, (id, status))

for agent, agent_information in agent_dictionary.items():
    if type(agent_information) is list:
        print(agent,agent_information)
