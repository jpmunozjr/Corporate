import csv
import re
from mysql import connector

dat_list = []

ad_db = connector.connect(
    host="IP_ADDRESS",
    user="ACCOUNT",
    passwd="PASSWORD",
    database="activedirectory"
)
ad_cursor = ad_db.cursor()

#Opens list of admin user names
with open("/path/ADUserNameList.txt") as file:
    #Queries each user name
    for username in file:
        #Replaces line breaks and extra space from user name text file for consistency
        username = (username.replace('\n', "")).strip()
        
        if re.match("^a-", username, re.IGNORECASE):
            ad_cursor.execute('SELECT DISTINCT mail,title FROM activedirectory.adaccounts WHERE samaccountname = "' + username[2:] + '"')
            ad_result = ad_cursor.fetchall()
        else:
            ad_cursor.execute('SELECT DISTINCT mail,title FROM activedirectory.adaccounts WHERE samaccountname = "' + username + '"')
            ad_result = ad_cursor.fetchall()
            
        try:
            email = str(ad_result[0][0])
        except:
            email = "None"
        try:
            title = str(ad_result[0][1])
        except:
            title = "None"
            
        dat_list.append(list([username,title,email]))
		
ad_cursor.close()
        
csvfile = r'/path/admin_emails.csv'
with open(csvfile, "wb") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(dat_list)