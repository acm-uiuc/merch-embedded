#!/bin/sh
# Needs Prod CA Key and CRT from Vaultwarden - ACM Infra - Vending Machine folder
read -p "Enter service name: " user
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr -subj "/C=US/ST=Illinois/L=Urbana/O=University of Illinois Urbana-Champaign/OU=Association for Computing Machinery - Production/CN=$user"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650 -sha256
rm client.csr ca.srl