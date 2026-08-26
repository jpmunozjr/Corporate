import re
import smtplib
import socket
import urllib
import urllib2
from elasticsearch import Elasticsearch, helpers
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mysql import connector

def groupMe(username,count):
    api_url = "https://api.groupme.com/v3/bots/post"
    message = "Admin Login Failure - Priority 1 - Username: %s, Count: %s" % (username,count)
    data = urllib.urlencode({"bot_id": "ID", "text": message})
    post = urllib2.urlopen(url=api_url, data=data)

def emailAlert(mailTo,subject,html):
    mailFrom = "EMAIL"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mailFrom
    msg['To'] = mailTo
    attachment = MIMEText(html, 'html')
    msg.attach(attachment)
    s = smtplib.SMTP("MAIL_SERVER")
    s.sendmail(mailFrom, mailTo, msg.as_string())
    s.quit()

es = Elasticsearch()

es_response = es.search(index="admin_login_failures-*",body={"size":0,"aggs":{"last_1_hour":{"date_range":{"field":"@timestamp","ranges":[{"from":"now-1h","to":"now"}]},"aggs":{"username_count":{"terms":{"field":"username","size":10000}}}}}})

for response in es_response['aggregations']['last_1_hour']['buckets']:
    for hit in response['username_count']['buckets']:
        username = str(hit['key'])
        count = int(hit['doc_count'])
        
        if count >= 15:
            groupMe(username,count)
        elif 15 > count >= 10:
            logins = []
            login_response = helpers.scan(client = es,scroll="5m",index="admin_login_failures-*",query={"size":1,"_source":["source_ip","destination_ip","event1"],"query":{"bool":{"must":[{"match":{"username":username}}],"filter":{"range":{"@timestamp":{"gte":"now-1h","lte":"now"}}}}}})
            for line in login_response:
                source_ip = str(line['_source']['source_ip'])
                destination_ip = str(line['_source']['destination_ip'])
                try:
                    source_host = (socket.gethostbyaddr(source_ip))[0]
                except:
                    source_host = "Could not resolve host."
                try:
                    destination_host = (socket.gethostbyaddr(destination_ip))[0]
                except:
                    destination_host = "Could not resolve host."
                logins.append(list([source_ip,source_host,destination_ip,destination_host]))
            
            logins = list(set(tuple(row) for row in logins))
            items = ["\n    <li>{}</li>".format(login) for login in logins]
            items = "".join(items)
        
            mailTo = "EMAIL"
            priority = "2"
            subject = "Admin Login Failures - Priority %s" % (priority)
            html = '<html><head></head><body>The user %s has triggered %s failed login events in the past hour from the following IPs:<br><br>Source IP - Source Host - Destination IP - Destination Host<br>%s<br><br>Please investigate.</body></html>' % (username,count,items) 
            emailAlert(mailTo,subject,html)
        elif 10 > count >= 5:
            ad_db = connector.connect(
                host="IP_ADDRESS",
                user="ACCOUNT",
                passwd="PASSWORD",
                database="activedirectory"
            )
            ad_cursor = ad_db.cursor()
            
            if re.match("^a-", username, re.IGNORECASE):
                ad_cursor.execute('SELECT DISTINCT mail,givenname FROM activedirectory.adaccounts WHERE samaccountname = "' + username[2:] + '"')
                ad_result = ad_cursor.fetchall()
            else:
                ad_cursor.execute('SELECT DISTINCT mail,givenname FROM activedirectory.adaccounts WHERE samaccountname = "' + username + '"')
                ad_result = ad_cursor.fetchall()
                
            try:
                email = str(ad_result[0][0])
            except:
                email = "None"
            try:
                name = str(ad_result[0][1])
            except:
                name = "None"
                
            logins = []
            login_response = helpers.scan(client = es,scroll="5m",index="admin_login_failures-*",query={"size":1,"_source":["source_ip","destination_ip","event1"],"query":{"bool":{"must":[{"match":{"username":username}}],"filter":{"range":{"@timestamp":{"gte":"now-1h","lte":"now"}}}}}})
            for line in login_response:
                source_ip = str(line['_source']['source_ip'])
                destination_ip = str(line['_source']['destination_ip'])
                try:
                    source_host = (socket.gethostbyaddr(source_ip))[0]
                except:
                    source_host = "Could not resolve host."
                try:
                    destination_host = (socket.gethostbyaddr(destination_ip))[0]
                except:
                    destination_host = "Could not resolve host."
                logins.append(list([source_ip,source_host,destination_ip,destination_host]))
            
            logins = list(set(tuple(row) for row in logins))
            items = ["\n    <li>{}</li>".format(login) for login in logins]
            items = "".join(items)
            
            if email == "None":
                mailTo = "EMAIL"
                priority = "3"
                subject = "Admin Login Failures - Priority %s - User Email Not Found" % (priority)
                html = '<html><head></head><body>The user %s has triggered %s failed login events in the past hour from the following IPs:<br><br>Source IP - Source Host - Destination IP - Destination Host<br>%s<br><br>Please manually notify user and update AD with a valid email address.</body></html>' % (username,count,items)            
                emailAlert(mailTo,subject,html)
            else:
                mailTo = email
                priority = "3"
                subject = "Admin Login Failures - Priority %s" % (priority)
                html = '<html><head></head><body>%s,<br><br>In an effort to be Helpful, Caring, and Responsive, we are informing you that our Automated Incident Response engine has noticed a trend in our logs.<br><br>The trend is as follows: %s failed login events generated from user %s from the IPs below --<br><br>Source IP - Source Host - Destination IP - Destination Host<br>%s<br><br>For any additional information, please contact IS Security at CORPISSECURITYENT@HCR-ManorCare.com.<br><br>Thank you for your time,<br>IS Security</body></html>' % (name,count,username,items)            
                emailAlert(mailTo,subject,html)
                
                mailTo = "EMAIL"
                subject = "Admin Login Failures - Priority %s - User Notified" % (priority)
                html = '<html><head></head><body>The user %s has triggered %s failed login events in the past hour from the following IPs:<br><br>Source IP - Source Host - Destination IP - Destination Host<br>%s<br><br>They have been notified successfully.</body></html>' % (username,count,items)            
                emailAlert(mailTo,subject,html)
        else:
            pass