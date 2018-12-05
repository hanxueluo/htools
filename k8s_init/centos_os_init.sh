#!/bin/bash
systemctl stop firewalld
systemctl disable firewalld

swapoff -a
sed -i '/\/dev\/mapper\/centos-swap /d' /etc/fstab 
#/dev/mapper/centos-swap swap                    swap    defaults        0 0
if ! grep -q hhl_root /etc/fstab;then
	echo '//172.16.70.1/hhl_root/   /root/hroot/ cifs defaults,username=root,password=1 0 0' >> /etc/fstab
fi

echo openvswitch >/etc/modules-load.d/openvswitch.conf
echo > /etc/modules-load.d/ipvs.conf
for m in ip_vs_sh ip_vs ip_vs_rr ip_vs_wrr nf_conntrack_ipv4
do
    modprobe $m
    echo $m >> /etc/modules-load.d/ipvs.conf
done

if ! test -f /etc/sysctl.d/k8s.conf;then
cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system
fi

echo "============"
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

yum install -y the_silver_searcher.x86_64
yum install -y bridge-utils
yum install -y vim git net-tools lsof nc tcpdump lsof strace cpio socat tcpdump telnet python wget cifs-utils ctags cscope conntrack-tools jq sshpass
yum install -y ipvsadm
yum install -y containernetworking-plugins


yum install -y docker
systemctl enable docker && systemctl start docker

if ! test -f /etc/yum.repos.d/kubernetes.repo;then
	cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF
fi

if test -f /etc/selinux/config;then
    setenforce 0
    sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
fi


k8sversion=-1.11.3-0
k8sversion=
yum install -y kubelet$k8sversion kubeadm$k8sversion kubectl$k8sversion --disableexcludes=kubernetes

systemctl enable kubelet && systemctl start kubelet


echo "==="
mkdir -p  /etc/cni/net.d/


