#!/bin/sh
#
# Bro Logs Backup
# Backs up the Bro Logs to the Security Share and then removes them from the server to save space.
rsync -av /data/zeek/zeek-3_0/logs/*-* /mnt/zeek_logs/
find /data/zeek/zeek-3_0/logs/20*-* -mtime +1 -exec rm -rf {} \;
