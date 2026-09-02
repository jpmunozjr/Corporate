import json
import requests

threats_url = "https://api.abnormalplatform.com/v1/threats?filter=receivedTime%20gte%202024-07-17T00%3A00%3A00Z%20lte%202024-07-17T23%3A59%3A59Z&pageSize=100&pageNumber=1&source=all"
headers = {"Authorization":"Bearer APOI_KEY","accept":"application/json"}

threats_response = requests.get(threats_url,headers=headers)
for line in threats_response.json()["threats"]:
    threat_id = line["threatId"]
    details_url = "https://api.abnormalplatform.com/v1/threats/" + threat_id
    
    details_response = requests.get(details_url,headers=headers)
    details = json.dumps(details_response.json())
    
    file_name = "threat-" + threat_id + ".json"
    with open(file_name, "w") as outfile:
        outfile.write(details)
