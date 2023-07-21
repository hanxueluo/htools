#!/bin/bash

function ip_to_int() {
	ip=$1
	IFS=. read -r a b c d <<< "$ip"
	printf '0x%02x%02x%02x%02x\n' $a $b $c $d
}

vport=8472

iip_src=0x2a:4
iip_dst=0x2e:4

itcp=0x32
itcp_src=0x32:2
itcp_dst=0x34:2

#####################
echo "udp and udp[$itcp_dst] == 123456"
exit
#ipi=$(ip_to_int 192.168.66.4)
echo tcpdump -nnr a.pcap -ttt -c 4 "udp and udp[$itcp_dst] == 44548"
exit
tcpdump -nnr a.pcap -ttt -c 4 "udp and (udp[$itcp_src] == 12345 or u"
#tcpdump -nnr a.pcap -ttt -c 4 "udp and udp[0x34:2] == 44548"
