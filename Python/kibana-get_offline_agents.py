import requests

linux_agents = []
windows_agents = []

url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents?perPage=1000&kuery=status%3Aoffline+AND+NOT+tags%3Adecommissioned+AND+last_checkin+%3C%3D+now-2d"
headers = {"Authorization":"ApiKey API_KEY"}

response = requests.get(url,headers=headers)
for agent in response.json()["list"]:
	try:
		if "linux" in agent["tags"]:
			linux_agents.append(agent["local_metadata"]["host"]["hostname"])
		elif "windows" in agent["tags"]:
			windows_agents.append(agent["local_metadata"]["host"]["hostname"])
	except:
		pass

print("LINUX AGENTS")
print(linux_agents)

print("WINDOWS AGENTS")
print(windows_agents)
