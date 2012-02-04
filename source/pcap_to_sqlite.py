#!/bin/sh

# pcap_to_sqlite.sh

# Generate the SQLite base.
# tcpdump and sqlite3 are needed.

if [ $# != 0 ] ; then
    capture=$1
else
    capture='./captures/jubrowska-capture_1.cap'
fi

echo "Reading the pcap file..."
tcpdump -r $capture -n -tt 'ip' |
cut -d" " -f1,3,5| sed -e 's/\([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\)\.[0-9]*/\1/g' |
sed -e 's/://g' > ./data/ip.data

echo "Creating SQLite base..."
echo "create table ip_link (tts real, ip_src text, ip_dst text);" |
sqlite3 ./data/ip.sql

while read ligne
do
set $(echo $ligne)
tts=$(eval echo $1)
ips=$(eval echo $2)
ipd=$(eval echo $3)
echo "insert into ip_link values('$tts','$ips','$ipd');" | sqlite3 ./data/ip.sql
done < ./data/ip.data

rm -f ./data/ip.data

exit 0
