import requests
from falconpy import Hosts

elastic_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents?kuery=NOT%20tags%3AFIX%20AND%20NOT%20status%3Aonline&perPage=500"
elastic_headers = {"Authorization":"ApiKey API_KEY"}
falcon_client_id = "CS_FCI"
falcon_client_secret = "CS_FCS"

list_of_agents_to_fix = []
list_of_agents_to_unenroll = []
falcon_hosts = Hosts(client_id=falcon_client_id,client_secret=falcon_client_secret)
elastic_response = requests.get(elastic_url,headers=elastic_headers)
for agent in elastic_response.json()["list"]:
	hostname = agent["local_metadata"]["host"]["name"]
	agent_id = agent["local_metadata"]["elastic"]["agent"]["id"]

	# Retrieve a list of hosts that have a hostname that matches our search filter
	hosts_search_result = falcon_hosts.query_devices_by_filter(filter=f"hostname:*'*{hostname}*'")

	# Confirm we received a success response back from the CrowdStrike API
	if hosts_search_result["status_code"] == 200:
		hosts_found = hosts_search_result["body"]["resources"]
		# Confirm our search produced results
		if hosts_found:
			print(hostname + " found in CrowdStrike; tagging as FIX.")
			list_of_agents_to_fix.append(agent_id)
		else:
			print(hostname + " not found in CrowdStrike; Agent ID added for unenrollment.")
			list_of_agents_to_unenroll.append(agent_id)
	else:
		# Retrieve the details of the error response
		error_detail = hosts_search_result["body"]["errors"]
		for error in error_detail:
			# Display the API error detail
			error_code = error["code"]
			error_message = error["message"]
			print(f"[Error {error_code}] {error_message}")

#tag as FIX
if len(list_of_agents_to_fix) > 0:
    print("Tagging " + str(len(list_of_agents_to_fix)) + " agents as FIX.")
    update_tags_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents/bulk_update_agent_tags"
    update_tags_headers = {"Authorization":"ApiKey API_KEY","Content-Type":"application/json","kbn-xsrf":"fleet_update_tags"}
    update_tags_body = {"agents":list_of_agents_to_fix,"tagsToAdd": ["FIX"]}
    update_tags_response = requests.post(update_tags_url,headers=update_tags_headers,json=update_tags_body)
    print(update_tags_response.json())
else:
    print("No agents to fix!")

#unenroll agents
if len(list_of_agents_to_unenroll) > 0:
    print("Unenrolling " + str(len(list_of_agents_to_unenroll)) + " agents.")
    unenroll_url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/api/fleet/agents/bulk_unenroll"
    unenroll_headers = {"Authorization":"ApiKey API_KEY","Content-Type":"application/json","kbn-xsrf":"fleet_unenroll"}
    unenroll_body = {"agents":list_of_agents_to_unenroll,"revoke":True,"force":True}
    unenroll_response = requests.post(unenroll_url,headers=unenroll_headers,json=unenroll_body)
    print(unenroll_response.json())
else:
    print("No agents to unenroll!")
