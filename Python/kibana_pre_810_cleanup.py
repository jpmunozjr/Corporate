import requests

url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents?kuery=tags%3AFIX&perPage=50"
headers = {"Authorization":"ApiKey API_KEY"}

response = requests.get(url,headers=headers)
for agent in response.json()["list"]:
	hostname = agent["local_metadata"]["host"]["name"]

	print(hostname)
