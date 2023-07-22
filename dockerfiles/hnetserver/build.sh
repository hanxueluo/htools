#!/bin/bash

VERSION=${1:-v8.0}
tag=vci-cn-beijing.cr.volces.com/vci-rd/hnet-public:$VERSION

finch build . -f Dockerfile -t "$tag"

#docker tag "$tag" net.cargo.io/library/hnet:$VERSION
