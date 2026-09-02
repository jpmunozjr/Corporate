from falconpy import Hosts

falcon_client_id = "FCI"
falcon_client_secret = "FCS"

hosts = Hosts(client_id=falcon_client_id,client_secret=falcon_client_secret)

with open('FILE.txt') as file:
    for line in file:
        #strips hidden newline off of text
        line = line.strip()

        # Retrieve a list of hosts that have a hostname that matches our search filter
        hosts_search_result = hosts.query_devices_by_filter(filter=f"hostname:*'*{line}*'")

        # Confirm we received a success response back from the CrowdStrike API
        if hosts_search_result["status_code"] == 200:
            hosts_found = hosts_search_result["body"]["resources"]
            # Confirm our search produced results
            if hosts_found:
                pass
            else:
                print(line)
        else:
            # Retrieve the details of the error response
            error_detail = hosts_search_result["body"]["errors"]
            for error in error_detail:
                # Display the API error detail
                error_code = error["code"]
                error_message = error["message"]
                print(f"[Error {error_code}] {error_message}")
