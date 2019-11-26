ARG BUILD_CONFIG='Release'

# Create a Release Build Base Image
FROM mcr.microsoft.com/dotnet/core/aspnet:3.0-buster-slim AS base-Release

WORKDIR /app
EXPOSE 80
EXPOSE 443

# Create a Debug Build Base Image
FROM mcr.microsoft.com/dotnet/core/aspnet:3.0-buster-slim AS base-Debug

# install 'ps' to support debugging to attached processes (do not use in production)
RUN apt update && apt install -y procps

# Add vsdbg to support debugging the container (do not use in production)
RUN apt update && \
    apt install unzip && \
    curl -sSL https://aka.ms/getvsdbgsh | /bin/sh /dev/stdin -v latest -l /vsdbg

WORKDIR /app
EXPOSE 80
EXPOSE 443

# Build
FROM mcr.microsoft.com/dotnet/core/sdk:3.0-buster AS build
RUN echo "$BUILD_CONFIG"
WORKDIR /src
COPY ["ElectionGuard.WebAPI.csproj", "./"]
RUN dotnet restore "./ElectionGuard.WebAPI.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "ElectionGuard.WebAPI.csproj" -c "$BUILD_CONFIG" -o /app/build

FROM build AS publish
RUN dotnet publish "ElectionGuard.WebAPI.csproj" -c "$BUILD_CONFIG" -o /app/publish

# Create Runtime Image
FROM base-${BUILD_CONFIG} AS final

WORKDIR /app
COPY --from=publish /app/publish .

ENTRYPOINT ["dotnet", "ElectionGuard.WebAPI.dll"]