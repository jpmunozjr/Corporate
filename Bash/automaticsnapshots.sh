#!/bin/bash

ADDRESS=localhost:9200
THIRTYDAYMARK=$(date -d "30 days ago" +"%s%3N") # gets tick value for this time two years ago. standard GNU command
#echo "30 day mark set at $THIRTYDAYMARK"
ARCHIVESNAPSHOTNAME="archive"
MAINBACKUP="es_backups"

echo "retrieving list of current indicies"

indices=$(curl -s -k https://$ADDRESS/_cat/indices?h=i,cd)
#indices=$(curl -s -u user:password -k https://$ADDRESS/_cat/indices?h=i,cd)

echo "retrival complete, entering archival loop"

while read -r OUTPUT 
do
    stringarray=($OUTPUT)

    indexname=${stringarray[0]}
    indexdate=${stringarray[1]}
    #echo ""
    #echo "indexname: $indexname, indexdate: $indexdate"
    if [ $indexdate -lt $THIRTYDAYMARK ]
    then        
        deleteindices=false
        if [[ $indexname != *"kibana"*  ]]
        then
            echo "index $indexname older than 30 days, archiving..."
            curl -XPUT -s -k https://$ADDRESS/_snapshot/$ARCHIVESNAPSHOTNAME/$indexname?wait_for_completion=true -H 'Content-Type: application/json' -d '{"indices": "'"$indexname"'", "ignore_unavailable": true, "include_global_state": false}'
			#curl -X PUT -s -u user:password -k https://$ADDRESS/_snapshot/$ARCHIVESNAPSHOTNAME/$indexname?wait_for_completion=true -H 'Content-Type: application/json' -d '{"indices": "'"$indexname"'", "ignore_unavailable": true, "include_global_state": false}'
			
			sleep 5

			currentBackup=$(curl -s -k https://$ADDRESS/_snapshot/$ARCHIVESNAPSHOTNAME/$indexname)
			#currentBackup=$(curl -s -u user:password -k https://$ADDRESS/_snapshot/$ARCHIVESNAPSHOTNAME/$indexname)
			if [[ $currentBackup == *'"state":"SUCCESS"'* ]]
			then
				deleteindices=true
			fi

			if [ "$deleteindices" = true ]           
			then
				echo ""
				echo "$indexname has been archived, deleting..."
				deleteindices=false
				curl -XDELETE -k https://$ADDRESS/$indexname
				#curl -X DELETE -u user:password -k https://$ADDRESS/$indexname
				echo ""
			fi
        fi
    fi
done <<< "$indices"

echo "---"
