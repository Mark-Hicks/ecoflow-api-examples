#!/bin/sh

# use EcoFlow API to show device info - https://developer-eu.ecoflow.com/us/document/introduction
# written by Sven Erbe - mail@sven-erbe.de - 30/01/2023 based of https://github.com/Mark-Hicks/ecoflow-api/blob/main/examples/Get-efAPI.ps1


URL="https://api.ecoflow.com"
QuotaPath="/iot-open/sign/device/quota/all"

# Replace with valid access/secret keys and device SN
accesskey="Fp4SvIprYSDPXtYJidEtUAd1o"
secretkey="WIbFEKre0s6sLnh4ei7SPUeYnptHG6V"
sn="DCABZ0123456789"

# generate nonce and timestamp

nonce=`echo $((RANDOM % (999999 - 100000 + 1) + 100000))`
timestamp=`echo $(date +"%s%3N")`

# str for generating of the signiture
str="sn=${sn}&accessKey=${accesskey}&nonce=${nonce}&timestamp=${timestamp}"

sign=`echo -n "${str}" | openssl dgst -sha256 -hmac "${secretkey}" -binary | od -An -v -tx1 | tr -d ' \n'`


curl -X GET "${URL}${QuotaPath}?sn=${sn}" \
-H "accessKey:${accesskey}" \
-H "timestamp:${timestamp}" \
-H "nonce:${nonce}" \
-H "sign:${sign}" \
-d '{"sn"="${sn}"}'
