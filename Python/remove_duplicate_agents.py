import requests
### VARIABLES ###
offline_count = 0
agent_dictionary = {}
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents"
url_modifiers = "?perPage=5000"
fleet_agent_url = url + url_endpoint + url_modifiers
headers = {"Authorization":"ApiKey API_KEY"}

### FUNCTIONS ###
def append_value(dict_obj, key, value):
    if key in dict_obj:
        if not isinstance(dict_obj[key], list):
            dict_obj[key] = [dict_obj[key]]
        dict_obj[key].append(value)
    else:
        dict_obj[key] = value

### SCRIPT ###
agents = requests.get(fleet_agent_url,headers=headers)
for record in agents.json()["list"]:
    #print(record)
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
        for record in agent_information:
            id = record[0]
            status = record[1]
            
            if status == "offline":
                delete_url = url + url_endpoint + "/" + id
                headers = {"kbn-xsrf": "curl", "Authorization":"ApiKey API_KEY"}
                delete_status = requests.delete(delete_url,headers=headers)
                print(delete_status.text)
