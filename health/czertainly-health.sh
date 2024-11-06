#!/bin/bash

set -e

URL_BASE='https://develop-02.czertainly.online/api/v1'
CLIENT_CRT=~/3K/client1.pem
CLIENT_KEY=~/3K/client1.key

echo -n "CZERTAINLY core: "
curl --silent --insecure --key "$CLIENT_KEY" --cert "$CLIENT_CRT" "$URL_BASE/health/liveness" | jq -r '.status'

echo "Components:"
curl --silent --insecure \
  --key $CLIENT_KEY --cert $CLIENT_CRT \
  "$URL_BASE/connectors" | jq -r '.[] | "\(.uuid) \(.name)"' | \
  # first get Connector UUID and than get it's health
  while read LN
  do
    UUID=`echo $LN | cut -d ' ' -f 1`
    NAME=`echo $LN | cut -d ' ' -f 2`

    URL="$URL_BASE/connectors/$UUID/health"
    STATUS=`curl --silent --insecure \
                --key $CLIENT_KEY --cert $CLIENT_CRT \
                $URL | jq -r '.status'`
    echo "  $NAME: $STATUS"
  done