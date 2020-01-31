.PHONY: build package run

# a phony dependency that can be used as a dependency to force builds
FORCE:

build: FORCE
	dotnet build

package:
	cd package/linux-x64 && ./package.sh

run:
	dotnet build
