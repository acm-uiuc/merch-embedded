#!/bin/sh
read -p "Enter user NetID (or other CN name): " user
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr -subj "/C=US/ST=Illinois/L=Urbana/O=University of Illinois Urbana-Champaign/OU=Association for Computing Machinery/CN=$user"
openssl x509 -req -in client.csr -CA config/ca.crt -CAkey config/ca.key -CAcreateserial -out client.crt -days 3650 -sha256
rm client.csr config/ca.srl