#!/bin/sh
# Properly quote the assignment of the COMMON_SUBJ variable
COMMON_SUBJ="/C=US/ST=Illinois/L=Urbana/O=University of Illinois Urbana-Champaign/OU=Development - Association for Computing Machinery/CN=development"

rm -rf config/*.crt config/*.key config/*.csr
mkdir -p config/
openssl genrsa -out config/ca.key 4096
openssl req -new -x509 -key config/ca.key -sha256 -out config/ca.crt -days 3650 -subj "$COMMON_SUBJ"

openssl genrsa -out config/server.key 4096
openssl req -new -key config/server.key -out config/server.csr -subj "$COMMON_SUBJ"
openssl x509 -req -in config/server.csr -CA config/ca.crt -CAkey config/ca.key -CAcreateserial -out config/server.crt -days 3650 -sha256

rm config/ca.srl config/server.csr