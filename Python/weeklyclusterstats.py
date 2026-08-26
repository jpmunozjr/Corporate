import datetime
import json
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

today = datetime.date.today()
week_ago = today - datetime.timedelta(days=7)
today = today.strftime("%m/%d/%Y")
week_ago = week_ago.strftime("%m/%d/%Y")

def email_alert(html):
    mailFrom = "EMAIL"
    mailTo = "EMAIL"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "ELK -- Weekly Throughput"
    msg['From'] = mailFrom
    msg['To'] = mailTo
    attachment = MIMEText(html, 'html')
    msg.attach(attachment)
    s = smtplib.SMTP("MAIL_SERVER")
    s.sendmail(mailFrom, mailTo, msg.as_string())
    s.quit()

command = "curl -X GET -s -u user:password -k 'https://server:9200/_cluster/stats?filter_path=indices.docs.count,indices.store.size_in_bytes'"
p = subprocess.Popen([str(command)], stdout=subprocess.PIPE, shell=True)
output, errors = p.communicate()
output = json.loads(output)

count = (int(output["indices"]["docs"]["count"])) / 30
count = "{:,}".format(count)

size = ((int(output["indices"]["store"]["size_in_bytes"])) / 1000000000) / 30

html = '<html><head></head><body>Thomas,<br><br>The throughput for the week spanning %s to %s is as follows:<br>     Average logs per day -- %s<br>     Average size per day -- %s GB<br><br>Thanks,<br>Your friendly neighborhood Elasticsearch</body></html>' % (week_ago,today,count,size)
email_alert(html)