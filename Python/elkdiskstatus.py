import datetime
import subprocess

count = 0
sum = 0
total_pct = []

print(datetime.date.today())

response = subprocess.Popen(['curl','-s','-k','https://SERVER:9200/_cat/allocation?v&s=node&h=node,disk.used,disk.percent'], stdout=subprocess.PIPE)
output, error = response.communicate()
output = output.split("\n")

for line in output[1:]:
	if line == '':
		pass
	else:
		count = count + 1
		line = (' '.join(line.split())).split(" ")
		
		node = line[0]
		used_size = line[1]
		used_pct = line[2]
		total_pct.append(used_pct)

for line in total_pct:
	sum = sum + int(line)
	
total_pct = sum / count

print(total_pct)