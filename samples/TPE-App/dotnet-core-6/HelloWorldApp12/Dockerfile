# Dotnet SDK Build Env:
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-env
WORKDIR /app

    # Copy csproj and restore as distinct layers
COPY ./app/*.csproj ./
RUN dotnet restore -r linux-arm

    # Copy everything else and build
COPY ./app ./
RUN dotnet publish -c release -o out -r linux-arm --self-contained false --no-restore

# Debian Stretch Env:
FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

FROM arm32v7/debian:stretch-slim as rootfs
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/
    # Install Moxa TagSDK Lib
RUN apt-get update \
  && apt-get install -q -y --fix-missing wget libicu-dev \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/mosquitto_1.6.8-1+un1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmosquitto1_1.6.8-1+un1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmosquitto-dev_1.6.8-1+un1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmx-dx1_1.0.2-1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmx-dx-dev_1.0.2-1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libparson-dev_1.1.0-1_armhf.deb \
  && wget https://tpe2.thingspro.io/tpe2/moxa-package/libparson1_1.1.0-1_armhf.deb \
  && apt-get install -f -y ./*.deb

    # Install aspnet runtime
WORKDIR /home/dotnet6
RUN wget https://download.visualstudio.microsoft.com/download/pr/93874c40-bd2d-4a7d-bbb5-716b161594c0/f698334222759b065f5da4e8915ae982/aspnetcore-runtime-6.0.2-linux-arm.tar.gz
RUN tar xzf aspnetcore-runtime-6.0.2-linux-arm.tar.gz -C /home/dotnet6
ENV PATH=$PATH:/home/dotnet6

    # Copy dotnet DLL to rootfs
WORKDIR /app
COPY --from=build-env /app/out .
RUN rm /usr/bin/qemu-arm-static

ENTRYPOINT ["dotnet", "HelloWorldApp12.dll"]
