#!/bin/bash

mkdir bin

cp -r ../../ElectionGuard.WebAPI/bin/Release/netcoreapp3.0/linux-x64/publish/* bin

tar -zcvf electionguard-api.tar.gz electionguard-api.service install_dependencies.sh bin data

rm -rf bin