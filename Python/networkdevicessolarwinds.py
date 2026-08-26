import cookielib
import csv
import getpass
import database_connection
import urllib
import urllib2
from bs4 import BeautifulSoup



###Scrapes SolarWinds All Nodes and APC UPS Inventory report tables for node name and IP address to save as CSV files in \\path\Reports\SolarWinds\###



###Variables###
login_username = "DOMAIN\\" + str(getpass.getpass(prompt="Username:"))
print(login_username)
login_password = str(getpass.getpass(prompt="Password:"))

#Login and file URLs
login_url = 'http://foo.com/'
allnodes_url = 'http://foo.com/'
apcupsinventory_url = 'http://foo.com/'

#HTTP request variables
req_headers = urllib.urlencode({
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
})

formdata = urllib.urlencode({
    'ctl00$BodyContent$Username': login_username,
    'ctl00$BodyContent$Password': login_password,
	'__VIEWSTATE': 'asdf'
	'__VIEWSTATEGENERATOR': 'asdf1234'
})

###Functions###

#Scrapes Report_All_Nodes and saves data into CSV
def allnodes_scrape():
	#Open All Nodes site and read HTML
	allnodes = opener.open(allnodes_url)
	allnodes_text = allnodes.read()
	
	#Extract table data tags from HTML
	soup = BeautifulSoup(allnodes_text, "lxml")
	allnodes_name = soup.find_all("td", { "class" : "qqp0_c0" })
	allnodes_ip = soup.find_all("td", { "class" : "qqp0_c2" })
	
	#Extract text from table data and group into usable list for CSV conversion
	allnodes_name_list = []
	for name in allnodes_name:
		allnodes_name_strip = name.get_text()
		allnodes_name_list.append(allnodes_name_strip)

	allnodes_ip_list = []	
	for ip in allnodes_ip:
		allnodes_ip_strip = ip.get_text()
		allnodes_ip_list.append(allnodes_ip_strip)
		
	allnodes_zipped_list = zip(allnodes_name_list, allnodes_ip_list)
	
	#Write to CSV file
	allnodes_csvfile = r'/path/Report_All_Nodes.csv'
	with open(allnodes_csvfile, "wb") as output:
		writer = csv.writer(output, lineterminator='\n')
		writer.writerows(allnodes_zipped_list)

#Insert Report_All_Nodes.csv into PRADS database and commit changes
def allnodes_insert():
	with open('/path/Report_All_Nodes.csv', 'r') as file:
		allnodes_csv = csv.reader(file)
		for row in allnodes_csv:
			nodename = row[0].lower()
			ipaddress = row[1].lower()
			sql = """REPLACE INTO `DATABASE`.`TABLE` (`system_name`,`ip_address`,`source`) VALUES ('%s','%s','%s')""" % (nodename, ipaddress, "solarwinds")
			database_connection.FUNCTION_NAME(sql)

#Scrapes Report_APC_UPS_Inventory and saves data into CSV
def apcupsinventory_scrape():
	#Open APC UPS Inventory site and read HTML
	apcupsinventory = opener.open(apcupsinventory_url)
	apcupsinventory_text = apcupsinventory.read()

	#Extract table data tags from HTML
	soup = BeautifulSoup(apcupsinventory_text, 'lxml')
	apcupsinventory_name = soup.find_all("td", { "class" : "qqp0_c1" })
	apcupsinventory_ip = soup.find_all("td", { "class" : "qqp0_c2" })

	#Extract text from table data and group into usable list for CSV conversion
	apcupsinventory_name_list = []
	for name in apcupsinventory_name:
		apcupsinventory_name_strip = name.get_text()
		apcupsinventory_name_list.append(apcupsinventory_name_strip)

	apcupsinventory_ip_list = []	
	for ip in apcupsinventory_ip:
		apcupsinventory_ip_strip = ip.get_text()
		apcupsinventory_ip_list.append(apcupsinventory_ip_strip)
		
	apcupsinventory_zipped_list = zip(apcupsinventory_name_list, apcupsinventory_ip_list)

	#Write to CSV file
	apcupsinventory_csvfile = r'/path/Report_APC_UPS_Inventory.csv'
	with open(apcupsinventory_csvfile, "wb") as output:
		writer = csv.writer(output, lineterminator='\n')
		writer.writerows(apcupsinventory_zipped_list)

#Insert Report_APC_UPS_Inventory into PRADS database and commit changes
def apcupsinventory_insert():
	with open('/path/Report_APC_UPS_Inventory.csv', 'r') as file:
		apcupsinventory_csv = csv.reader(file)
		for row in apcupsinventory_csv:
			nodename = row[0].lower()
			ipaddress = row[1].lower()
			sql = """REPLACE INTO `DATABASE`.`TABLE` (`system_name`,`ip_address`,`source`) VALUES ('%s','%s','%s')""" % (nodename, ipaddress, "solarwinds")
			database_connection.FUNCTION_NAME(sql)

###Program###

#Build opener w/ cookies, log in to SolarWinds
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login = opener.open(login_url, formdata)

#Scrape SolarWinds tables
allnodes_scrape()
apcupsinventory_scrape()

#Insert table data into PRADS database
allnodes_insert()
apcupsinventory_insert()
