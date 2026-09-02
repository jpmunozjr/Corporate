import json
import requests

indices = ["INDEX1","INDEX2"]
url = "https://DEPLOYMENT.eastus2.azure.elastic-cloud.com/"
rollover_endpoint = "/_rollover"
reindex_endpoint = "_reindex?wait_for_completion=false"
reindex_url = url + reindex_endpoint
headers = {'content-type': 'application/json'}

for index in indices:
    #rollover
    #data_stream = (index.split(".ds-")[1]).split("-2")[0]
    #rollover_url = url + data_stream + rollover_endpoint
    #rollover_response = requests.post(rollover_url, auth=("USER","PASS"))

    #put reindex index
    #reindex_name = index + "-reindex"
    #put_url = url + reindex_name
    #put_response = requests.put(put_url, auth=("USER","PASS"))

    #reindex
    #reindex_data = json.dumps({"source":{"index":index},"dest":{"index":reindex_name}})
    #reindex_response = requests.post(reindex_url, headers=headers, data=reindex_data, auth=("USER","PASS"))
    #print(reindex_response.json())
    
    #check reindex status
    
    #delete
    delete_url = url + index
    delete_response = requests.delete(delete_url, auth=("USER","PASS"))
    print(delete_response.json())
