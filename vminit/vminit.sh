#!/bin/bash


PATTERN=$1 # centos
IPSUFFIX=$2  # 70.100


if ! test -f xmls/$PATTERN.xml ;then
    echo "pattern xmls/$PATTERN.xml doesn't exist"
    exit 1
fi

if ! echo $IPSUFFIX |grep -q '^7[0-5]\.[0-9]\+' ;then
    echo "invalid ip postfix: $IPSUFFIX"
    exit
fi

IPPREFIX=172.19
IMAGE_DIR=/vms/ssdimages
IMAGE_DIR=/vms/images

BASE_IMAGE=centos7.7.qcow2
BASE_DATA_IMAGE=centos-data.qcow2
BASE_IMAGE=ubuntu.qcow2
BASE_DATA_IMAGE=

#
IP=$IPPREFIX.$IPSUFFIX
VMNAME=$(echo v$IPSUFFIX| sed 's/\./v/g')


init_xml() {
    if test -f /etc/libvirt/qemu/$VMNAME.xml;then
        return
    fi

    local images1=$IMAGE_DIR/$VMNAME.qcow2
    local images2=$IMAGE_DIR/$VMNAME-data.qcow2

    sed "s,@NAME@,$VMNAME,g" xmls/$PATTERN.xml > /tmp/$VMNAME.xml
    sed -i "s,@IMAGE@,$images1,g" /tmp/$VMNAME.xml
    sed -i "s,@IMAGE2@,$images2,g" /tmp/$VMNAME.xml
    virsh define /tmp/$VMNAME.xml
}

init_disk() {
    (
        cd $IMAGE_DIR
        qemu-img create -f qcow2 vm--$VMNAME -b $BASE_IMAGE
        mv vm--$VMNAME $VMNAME.qcow2

        if [ -n "$BASE_DATA_IMAGE" ];then
            cp $BASE_DATA_IMAGE $VMNAME-data.qcow2
        fi
    )
}

_init_netlan() {
	local ip=$1
    cat <<EOF
# This is the network config written by 'subiquity'
network:
  version: 2
  ethernets:
    ens3:
            dhcp4: no
            addresses: [$ip/16]
            gateway4: 172.19.0.253
            nameservers:
                    addresses: [192.168.33.251]
EOF
}

init_inside_files() {
    local hostname=host-$VMNAME
    rm -rf rootfs2 vm-init.tar
    cp -a rootfss/$PATTERN rootfs2

    if [ "$PATTERN" = centos ];then
        (
            cd  rootfs2
            sed -i "s/@HOSTNAME@/$hostname/g" etc/hosts etc/hostname
            sed -i "s/@IP@/$IP/g" etc/sysconfig/network-scripts/*
        )
    elif [ "$PATTERN" = ubuntu ];then
        (
            cd  rootfs2
            sed -i "s/@HOSTNAME@/$hostname/g" etc/hosts etc/hostname
			_init_netlan $IP > etc/netplan/05-netcfg.yaml
		)
    fi
    tar vcf vm-init.tar -C rootfs2 ./
}

clean_file() {
    rm -rf rootfs2 vm-init.tar
}


makesure_shutdown() {
    if virsh list --name | grep -xq "$VMNAME" ;then
        echo Error: $VMNAME is still running, please shutdown first
        echo = virsh shutdown $VMNAME
        echo = virsh destroy $VMNAME
        exit 1
    fi
}


makesure_shutdown

init_xml
init_disk
init_inside_files
virt-tar-in -d $VMNAME vm-init.tar /

clean_file

virsh start $VMNAME
virsh vncdisplay $VMNAME

echo ssh $IP
