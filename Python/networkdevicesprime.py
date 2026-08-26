import csv
import os
import database_connection
import re

#################
### Variables ###
#################

#Path to the Prime files
path = "/path/reports/Prime"
#List of device names, mac addresses, and IP addresses
dataList = []

###############
### Program ###
###############

#Iterate through every file in path
for filename in os.listdir(path):
	#Open the file
	with open(path + "/" + filename) as file:
		#Read the file
		reader = csv.reader(file)
		#Add file lines to fileList
		fileList = list(reader)
	#Iterate through fileList
	for line in fileList:
		try:
			#Look for IP address regex in 2nd column
			if re.match("^(10.|172.)", line[1]):
				#Append name and IP address to dataList
				dataList.append(list([line[0], line[1]]))
				continue
		#Skip lines without appropriate length (mostly header files)
		except IndexError:
			pass
		try:
			#Look for IP address regex in 3rd column
			if re.match("^(10.|172.)", line[2]):
				#Append name and IP address to dataList
				dataList.append(list([line[0], line[2]]))
				continue
		#Skip lines without appropriate length (mostly header files)
		except IndexError:
			pass

#Iterate through dataList			
for line in dataList:
	#Name and IP address
	name = line[0]
	ip = line[1]

	#Insert name and IP address into database
	sql = """REPLACE INTO `foo`.`foo` (`system_name`,`ip_address`,`source`) VALUES ('%s','%s','%s')""" % (name, ip, "prime")
	database_connection.FUNCTION_NAME(sql)

