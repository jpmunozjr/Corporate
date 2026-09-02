import requests

### Variables ###
# change these
elastic_api_key = "API_KEY"
# do not change these
alert_id = "ALERT_ID"
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/ALERT_INDEX/_update/" + alert_id
auth = "ApiKey " + elastic_api_key
headers = {"kbn-xsrf":"true","Content-Type":"application/json","Authorization":auth}
action = "open"
body = {"doc":{"kibana.alert.workflow_status":action}}

http_response = requests.post(url,headers=headers,json=body)
json_response = http_response.json()
print(http_response.status_code)

#successful post request
if http_response.status_code == 200:
    #status updated
    if json_response["result"] == "updated":
        print("Successfully Updated.")
    #status not changed
    elif json_response["result"] == "noop":
        print("Status has already been set.")
#document not found
elif http_response.status_code == 404:
    print(http_response.text)
#all other errors
else:
    print(http_response.text)
