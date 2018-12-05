

#echo > /etc/modules-load.d/ipvs.conf
#for m in ip_vs_sh ip_vs ip_vs_rr ip_vs_wrr nf_conntrack_ipv4
#do
#    modprobe $m
#    echo $m >> /etc/modules-load.d/ipvs.conf
#done


kubeadm init --pod-network-cidr=172.21.0.0/16 |tee init.log
tail init.log |grep join > join
rm -f init.log
echo kubectl taint nodes --all node-role.kubernetes.io/master-
exit
#kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl apply -f https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/hosted/canal/rbac.yaml
kubectl apply -f https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/hosted/canal/canal.yaml

