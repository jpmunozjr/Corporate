import gearman
import HIDSDatabase
import json
import re
#import smtplib
import socket
import subprocess
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

#################
### Variables ###
#################

personalInfoList = ['credit card', 'ssn']
scanList = ['adware', 'dshield', 'dyre', 'et cins', 'etpro cins', 'et cnc', 'etpro cnc', 'et exploit', 'etpro exploit', 'et malware', 'etpro malware', 'et trojan', 'etpro trojan', 'image file', 'likely hostile', 'likely malware', 'often malware', 'ransomware', 'shadowserver', 'soceng', 'toolbar']
redFlags = []

#################
### Functions ###
#################

#Search /var/log/suricata/fast.log for keywords and parse out data
def alertHunter(target):
	replace = ['[', ']', '\n']
	#Search suricata fast.log for alerts within the past minute
	output = subprocess.Popen(['grep "$(date -d "1 minute ago" +"%m/%d/%Y-%H:%M")" -A 999999 /var/log/suricata/fast.log'], stdout=subprocess.PIPE, shell=True)
	#keywords in all cases
	targetVariants = [target.title(), target.upper(), target.lower()]

	#Search lines from fast.log for keywords
	for line in iter(output.stdout.readline, ''):
		try:
			for variant in targetVariants:
				if variant in line:
					for character in replace:
						if character in line:
							line = line.replace(character, ' ')
					#Parse out timestamp, signature, classification, priority, source IP, and destination IP
					timestamp = line.split('  ')[0].strip()
					signature = line.split('  ')[3].strip()
					classification = (line.split('  ')[5]).split(':')[1].strip()
					priority = (line.split('  ')[6]).split(':')[1].strip()
					srcIP = (line.split(' ')[-4]).split(':')[0].strip()
					dstIP = (line.split(' ')[-2]).split(':')[0].strip()
					#Infoblox whitelist
					if srcIP == 'IP_ADDRESS' or dstIP == 'IP_ADDRESS':
						pass
					elif srcIP == 'IP_ADDRESS' or dstIP == 'IP_ADDRESS':
						pass
					#Don't process duplicate signatures
					elif redFlags == []:
						redFlags.append(list([target, timestamp, signature, classification, priority, srcIP, dstIP]))
					else:
						for line in redFlags:
							if signature == redFlags[2] and srcIP == redFlags[5] and dstIP == redFlags[6]:
								pass
							else:
								#Add into list
								redFlags.append(list([target, timestamp, signature, classification, priority, srcIP, dstIP]))
		except:
			pass

#Send email to ERM if keyword has been found
#def emailAlert(target, timestamp, signature, classification, priority, srcIP, dstIP):
#	scannerHostname = (socket.gethostname()).upper()
#	try:
#		srcHostname = socket.gethostbyaddr(srcIP)[0]
#	except:
#		srcHostname = 'Could not resolve host name.'
#	try:
#		dstHostname = socket.gethostbyaddr(dstIP)[0]
#	except:
#		dstHostname = 'Could not resolve host name.'
#	mailFrom = "EMAIL"
#	mailTo = "EMAIL"
#	msg = MIMEMultipart('alternative')
#	msg['Subject'] = "%s - Alert: %s Activity Detected" % (scannerHostname, target)
#	msg['From'] = mailFrom
#	msg['To'] = mailTo
#	html = '<html><head></head><body><p><b><u>%s Activity Detected:</u></b><br>%s - %s - Classification: %s - Priority: %s - (%s -> %s)<br><br><b><u>Source IP Address Information:</u></b><br>%s = %s<br><br><b><u>Destination IP Address Information:</u></b><br>%s = %s</p></body></html>' % (target, timestamp, signature, classification, priority, srcIP, dstIP, srcIP, srcHostname, dstIP, dstHostname)
#	attachment = MIMEText(html, 'html')
#	msg.attach(attachment)
#	s = smtplib.SMTP("EMAIL_SERVER")
#	s.sendmail(mailFrom, mailTo, msg.as_string())
#	s.quit()

#Submit malware jobs to SERVER
def malwareScan(jobSpecs):
    gearmanServer = "SERVER:4735"
    gearmanClient = gearman.GearmanClient([gearmanServer])
    malwareJob = gearmanClient.submit_job('malware', json.dumps(jobSpecs))

###############
### Program ###
###############

#Search fast.log for keywords
for keyword in (personalInfoList + scanList):
	alertHunter(keyword)

#Handle keywords matches
for alert in redFlags:
	target = alert[0]
	timestamp = alert[1]
	signature = alert[2]
	classification = alert[3]
	priority = alert[4]
	srcIP = alert[5]
	dstIP = alert[6]
	#Sends email and adds entry into database if destination IP isn't 172.
	if target in personalInfoList:
		if re.match("^172.", dstIP):
			pass
		else:
			#emailAlert(target.upper(), timestamp, signature, classification, priority, srcIP, dstIP)
			sql = """INSERT INTO `DATABASE_NAME`.`TABLE_NAME` (`timestamp`, `signature`, `classification`, `priority`, `sourceip`, `destinationip`) VALUES ('%s','%s','%s','%s','%s','%s')""" % (timestamp, signature, classification, priority, srcIP, dstIP)
			HIDSDatabase.FUNCTION_NAME(sql)
	#Sends email and starts malware scan if source IP is 172. or 10.
	elif target in scanList:
		if re.match("^(10.|172.)", srcIP):
			#emailAlert(target.upper(), timestamp, signature, classification, priority, srcIP, dstIP)
			jobSpecs = [srcIP, signature]
			malwareScan(jobSpecs)
		else:
			continue
	else:
		pass
