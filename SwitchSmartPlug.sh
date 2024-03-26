#!/bin/sh

# use EcoFlow API to switch a Ecoflow Smart Plug - https://developer-eu.ecoflow.com/us/document/introduction
# written by Sven Erbe - mail@sven-erbe.de - 30/01/2023 based of https://github.com/Mark-Hicks/ecoflow-api/blob/main/examples/Get-efAPI.ps1


URL="https://api.ecoflow.com"
QuotaPathALL="/iot-open/sign/device/quota/all"
QuotaPath="/iot-open/sign/device/quota"

# Replace with valid access/secret keys and device SN

accesskey="Fp4SvIprYSDPXtYJidEtUAd1o"
secretkey="WIbFEKre0s6sLnh4ei7SPUeYnptHG6V"
sn="HWABZ0123456789"

cmdCode="WN511_SOCKET_SET_PLUG_SWITCH_MESSAGE"

params="plugSwitch=1"
body="{\"sn\":\"${sn}\",\"cmdCode\":\"${cmdCode}\",\"params\":{\"plugSwitch\":1}}"

# generate nonce and timestamp

nonce=`echo $((RANDOM % (999999 - 100000 + 1) + 100000))`
timestamp=`echo $(date +"%s%3N")`

# str for generating of the signiture
str="cmdCode=${cmdCode}&params.${params}&sn=${sn}&accessKey=${accesskey}&nonce=${nonce}&timestamp=${timestamp}"

sign=`echo -n "${str}" | openssl dgst -sha256 -hmac "${secretkey}" -binary | od -An -v -tx1 | tr -d ' \n'`


curl -X PUT "${URL}${QuotaPath}?sn=${sn}" \
-H 'Content-Type:application/json;charset=UTF-8' \
-H "accessKey:${accesskey}" \
-H "timestamp:${timestamp}" \
-H "nonce:${nonce}" \
-H "sign:${sign}" \
-d $body 
``
