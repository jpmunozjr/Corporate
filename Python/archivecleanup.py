import subprocess

filename = '/path/old_archive.txt'

with open(filename) as f:
    for line in f:
		line = line.strip()
		
		command = "curl -X DELETE -s -u user:password -k 'https://SERVER:9200/_snapshot/archive/" + line + "'"
		p = subprocess.Popen([str(command)], stdout=subprocess.PIPE, shell=True)
		output, errors = p.communicate()
		print(output)
		#print(command)