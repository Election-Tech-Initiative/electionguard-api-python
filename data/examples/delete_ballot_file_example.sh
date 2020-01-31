#!/bin/bash

curl -X DELETE \
  'http://localhost:5000/electionguard/BallotFile?fileName=encrypted-ballots_2020_1_30' \
  -H 'Accept: */*' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 0' \
  -H 'Host: localhost:5000' \
  -H 'cache-control: no-cache'