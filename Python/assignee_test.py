import requests
alertid = "ALERT_ID"
status = "acknowledged"
owner = "USER"

elastic_assignee_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/_security/profile/_suggest"
elastic_assignee_body = {"size":1,"name":owner}
elastic_security_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/ALERT_INDEX/_update/" + alertid
headers = {"Authorization":"ApiKey API_KEY","Content-Type":"application/json"}

http_assignee = requests.get(elastic_assignee_url,headers=headers,json=elastic_assignee_body)
json_assignee = http_assignee.json()
print(json_assignee)
#assignee_id = json_assignee["profiles"][0]["uid"]
