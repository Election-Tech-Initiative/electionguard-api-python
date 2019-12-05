!#/usr/bin/bash

mkdir bin

cp -r ../../ElectionGuard.WebAPI/bin/Release/netcoreapp3.0/linux-x64/publish/* bin

tar -zcvf electionguard-api.tar.gz electionguard-api.service bin

rm -rf bin