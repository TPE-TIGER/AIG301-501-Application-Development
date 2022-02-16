FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-env
WORKDIR /app

COPY *.csproj ./
RUN dotnet restore -r linux-arm

COPY . ./
RUN dotnet publish -c Release -o out -r linux-arm --self-contained false --no-restore

FROM mcr.microsoft.com/dotnet/runtime:6.0-bullseye-slim-arm32v7
WORKDIR /app
COPY --from=build-env /app/out ./


ENTRYPOINT ["dotnet", "SampleModule.dll"]
