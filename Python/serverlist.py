import PRADSDatabase
import re
import subprocess

#################
### VARIABLES ###
#################

subnets = ["IP1/24", "IP2/24"]
pattern = re.compile("^111.1[11].111.[111]$")

for subnet in subnets:
	ip_command = 'nmap -sn ' + subnet + ' | grep report'
	active_ips = subprocess.Popen([str(ip_command)], stdout=subprocess.PIPE, shell=True)
	for line in iter(active_ips.stdout.readline, ""):
		line = line.replace("\n","")
		
		if "(" in line:
			line = (line.split("for "))[1]
			hostname = (line.split(" "))[0]
			ip = (((line.split(" "))[1]).replace("(","")).replace(")","")
			
			#KNOWN
			if ("foo" in hostname) or ("foo" in hostname) or ("foo" in hostname):
				os = "linux"
			elif ("foo" in hostname) or ("foo" in hostname):
				os = "windows"
			else:
				os = None
			
			if pattern.match(ip):
				pass
			elif os != None:
				pass
			else:
				os_command = 'nmap -O ' + ip
				os_type = (subprocess.Popen([str(os_command)], stdout=subprocess.PIPE, shell=True)).communicate()

				if ("windows" in str(os_type)) or ("Windows" in str(os_type)):
					os = "windows"
				elif ("linux" in str(os_type)) or ("Linux" in str(os_type)):
					os = "linux"
				else:
					os = "other"
					
			print(hostname,ip,os)
			sql = """Insert INTO `foo`.`foo` (`hostname`,`ipaddress`, operating_system) VALUES ('%s','%s','%s')""" % (hostname,ip,os)
			PRADSDatabase.FUNCTION_NAME(sql)
		else:
			hostname = None
			ip = (line.split("for "))[1]
			
			if pattern.match(ip):
				pass
			else:
				os_command = 'nmap -O ' + ip
				os_type = (subprocess.Popen([str(os_command)], stdout=subprocess.PIPE, shell=True)).communicate()

				if ("windows" in str(os_type)) or ("Windows" in str(os_type)):
					os = "windows"
				elif ("linux" in str(os_type)) or ("Linux" in str(os_type)):
					os = "linux"
				else:
					os = "other"
					
				print(hostname,ip,os)
				sql = """Insert INTO `foo`.`foo` (`hostname`,`ipaddress`, operating_system) VALUES ('%s','%s','%s')""" % (hostname,ip,os)
				PRADSDatabase.FUNCTION_NAME(sql)