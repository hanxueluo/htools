



ip link del vxlan100
lid=1
rid=2
vtep=172.16.70.7$lid
remote_vtep=172.16.70.7$rid

local_dstveth=100.100.$lid
remote_dstveth=100.100.$rid

mac=4a:1e:20:a0:00:0

ip link add vxlan100 type vxlan dstport 4788 id 100 local $vtep nolearning
ip link set vxlan100 address $mac$lid

ip addr add $local_dstveth.1/32 dev vxlan100
ip link set vxlan100 up

ip route add $remote_dstveth.0/24 via $remote_dstveth.1 dev vxlan100 onlink

rid=3
ip ne replace $remote_dstveth.1 dev vxlan100 lladdr $mac$rid
bridge fdb replace $mac$rid dev vxlan100 dst $remote_vtep self permanent

ping 100.100.2.4
