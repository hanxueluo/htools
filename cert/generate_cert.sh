#!/bin/bash


domain=${1:-test.netlb.com}

gen() {
    local domain=$1

    cakey=ca.key
    cacrt=ca.crt
    servercrt=server.crt
    outlog=out.log

    mkdir -p ./tmp_cert/
    (
        cd ./tmp_cert/

        rm -f $cakey $cacrt $servercrt
        subject="/C=CN/ST=Zhejiang/L=Hangzhou/O=BD/OU=Cloud/CN=$domain/emailAddress=hanxueluo@gmail.com"

        openssl genrsa -out $cakey 4096
        openssl req -new -nodes -key $cakey -out $cacrt -sha256 -subj "$subject"
        openssl x509 -req -sha256 -days 7304 -in $cacrt -signkey $cakey -out $servercrt

        # display result
        openssl x509 -in $servercrt -noout -text | tee $outlog
        cd -
    )
    local dir="${domain/\*/_}"

    if test -f ./tmp_cert/$outlog;then
        mkdir -p $dir
        mv ./tmp_cert/* $dir
        rm -rf ./tmp_cert/
    fi
}

gen $domain
