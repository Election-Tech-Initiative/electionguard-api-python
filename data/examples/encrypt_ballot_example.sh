#!/bin/bash

curl -X POST \
  http://localhost:5000/electionguard/EncryptBallot \
  -H 'Accept: */*' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 225' \
  -H 'Content-Type: application/json' \
  -H 'Host: localhost:5000' \
  -H 'cache-control: no-cache' \
  -d '{
    "ballot": {
    	"ballotId": "000-000-001",
		"ballotStyle": {
			"id": "1"
		},
		"votes": {
			"justice-supreme-court" : [
				{
					"id": "laurel-clark"
					
				}
			],
			"referendum-michigan-up" : "yes"
		}
	}
}'