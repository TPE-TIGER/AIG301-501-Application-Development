# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-env
WORKDIR /app

# Copy csproj and restore as distinct layers
COPY ./app/*.csproj ./
RUN dotnet restore -r linux-arm

# Copy everything else and build
COPY ./app ./
RUN dotnet publish -c release -o out -r linux-arm --self-contained false --no-restore

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:6.0-bullseye-slim-arm32v7
WORKDIR /app
COPY --from=build-env /app/out .
ENTRYPOINT ["dotnet", "HelloWorldApp10.dll"]
