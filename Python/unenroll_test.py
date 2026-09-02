import requests

agent_id = ["AGENT_ID"]

unenroll_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents/bulk_unenroll"
unenroll_headers = {"Authorization":"ApiKey API_KEY","Content-Type":"application/json","kbn-xsrf":"fleet_unenroll"}
unenroll_body = {"agents":agent_id,"revoke":True,"force":True}
unenroll_response = requests.post(unenroll_url,headers=unenroll_headers,json=unenroll_body)
print(unenroll_response.json())
