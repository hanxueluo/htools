FROM cargo.caicloudprivatetest.com/library/socket_python:x0

LABEL maintainer="Huanle Han <hanhuanle@caicloud.io>"

WORKDIR /Common_file

#COPY ./Common_file/ /
COPY ./Common_file/http2.py /Common_file/
COPY ./Common_file/start_socket.sh /Common_file/

ENTRYPOINT ["sh", "/Common_file/start_socket.sh"]

EXPOSE 80
