import datetime
import json
import requests
import socket
import time

#################
### VARIABLES ###
#################

### Auth Token Variables ###
client_id = "1d4fbea7-foo"
scope = "https%3A%2F%2Fgraph.microsoft.com%2F.default"
client_secret = "foowU1zUcol33"
grant_type = "client_credentials"
body = "client_id=" + client_id + "&scope=" + scope + "&client_secret=" + client_secret + "&grant_type=" + grant_type
auth_url = 'https://login.microsoftonline.com/foo.onmicrosoft.com/oauth2/v2.0/token'

### Query Variables ###
count = 0
break_loop = None
one_hour_ago = ((datetime.datetime.utcfromtimestamp(time.time())) - datetime.timedelta(hours=1)).isoformat()
#url = "https://graph.microsoft.com/v1.0/auditLogs/AuditLogs"
query_url = 'https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge ' + str(one_hour_ago) + 'Z'
#query_url = 'https://graph.microsoft.com/v1.0/auditLogs/signIns'
beta_url = 'https://graph.microsoft.com/beta/auditLogs/signIns?$filter=createdDateTime ge ' + str(one_hour_ago) + 'Z'


#################
### FUNCTIONS ###
#################

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
    
def generate_token(url, body):
    auth_request = requests.post(url = url, data = body)
    auth_response = auth_request.json()
    print(auth_response)
    return auth_response['access_token']
    
def query(access_token, url):
    query_header = {'Content-Type': 'application\json', 'Authorization': access_token}
    query_request = requests.get(url = url, headers = query_header)
    query_response = json.loads(query_request.text)
    
    try:
        next_url = query_response['@odata.nextLink']
    except:
        next_url = None
    
    print(next_url)
    
    return next_url, query_response['value']
    
def send_to_elk(data):
    stream_socket = socket.socket()
    stream_socket.connect(('IP_ADDRESS', 5044))
    stream_socket.sendall(json.dumps(data))
    stream_socket.close()

###############
### PROGRAM ###
###############

while query_url != None:
    try:
        query_url, query_results = query(access_token, query_url)
        for result in query_results:
            result = flatten_json(result)
            send_to_elk(result)
        
    except (KeyError, NameError):
        access_token = generate_token(auth_url, body)

print("DONE: Regular")

while beta_url != None:
    try:
        beta_url, query_results = query(access_token, beta_url)
        
        for result in query_results:
            result = flatten_json(result)
            send_to_elk(result)
        
    except (KeyError, NameError):
        access_token = generate_token(auth_url, body)

print("DONE: Beta")
