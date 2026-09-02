import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union

### Variables ###
# Dynamic
xsoar_api_key_id = "API_KEY_ID"
xsoar_api_key = "API_KEY"
# Static
xsoar_headers = {"x-xdr-auth-id":xsoar_api_key_id,"Authorization":xsoar_api_key,"Content-Type":"application/json"}
xsoar_base_url = "XSOAR_URL"

# Classes
class Comment(BaseModel):
    field: Union[str, None] = None

class Update(BaseModel):
    # defines the POST body for Elastic update requests
    details: Union[str, None] = None
    elastic_id: Union[str, None] = None
    id: Union[str, None] = None
    name: Union[str, None] = None
    severity: Union[str, None] = None
    status: Union[str, None] = None
    tags: Union[list, None] = None
    xsoar_id: Union[str, None] = None
    version: Union[int, None] = None

### Endpoints ###
app = FastAPI()

@app.post("/create_case")
async def create_case():
    import requests
    
    xsoar_endpoint = "/xsoar/public/v1/incident"
    xsoar_full_url = xsoar_base_url + xsoar_endpoint
    xsoar_body = {"name":"Test API Case","details":"This is an API test.","type":"Unclassified","createInvestigation":True}
    response = requests.post(xsoar_full_url,headers=xsoar_headers,json=xsoar_body)
    return response

### Program ###
if __name__ == "__main__":
    uvicorn.run("xsoar_case_management_api:app",port=8000,host="0.0.0.0",reload=True)
