import requests

policy_search = "AGENT_POLICY"
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
url_endpoint = "api/fleet/agents/"
url_modifiers = "?perPage=10000"
fleet_agent_url = url + url_endpoint + url_modifiers

agents = requests.get(fleet_agent_url,auth=("USER","PASS"))
for record in agents.json()["list"]:
    try:
        policy_id = record["policy_id"]
    except:
        policy_id = None
    
    if policy_id == policy_search:
        try:
            status = record["status"]
        except:
            status = None
        
        if status == "offline":
            try:
                id = record["id"]
            except:
                id = None
            
            delete_url = url + url_endpoint + id
            delete_status = requests.delete(delete_url,auth=("USER","PASS"),headers={"kbn-xsrf": "curl"})
            print(delete_status.text)
