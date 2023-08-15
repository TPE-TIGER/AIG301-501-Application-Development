#----
FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

################################################################################
# BUILD
################################################################################
FROM arm32v7/debian:stretch-slim as build
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/
COPY . /app
WORKDIR /app

# Build ulfius (web backend)
RUN apt update \
    && apt install -y build-essential git cmake libmicrohttpd-dev libjansson-dev libcurl4-gnutls-dev libgnutls28-dev libgcrypt20-dev zlib1g-dev libsystemd-dev \
    && rm -rf /var/lib/apt/lists/* \
    && git clone https://github.com/babelouest/ulfius.git -b v2.7.3 \
    && cd ulfius && mkdir build && cd build \
    && cmake .. && make && make install

# Install TPE libraries
RUN apt update \
    && apt install -y libprotobuf-c1 wget \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libparson1_1.1.0-1_armhf.deb \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libparson-dev_1.1.0-1_armhf.deb \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmosquitto-dev_1.6.8-1%2Bun1_armhf.deb \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmosquitto1_1.6.8-1%2Bun1_armhf.deb \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmx-dx1_1.0.2-1_armhf.deb \
    && wget https://tpe2.thingspro.io/tpe2/moxa-package/libmx-dx-dev_1.0.2-1_armhf.deb \
    && dpkg -i *.deb \
    && rm *.deb

# Compile Our Code
RUN gcc app/app.c -o app.o -lmx-dx -lulfius -ljansson -lcurl

###############################################################################
# TARGET
##############################################################################
FROM arm32v7/debian:stretch-slim as target
COPY --from=build /usr/bin/qemu-arm-static /usr/bin/
COPY --from=build /usr/local/lib/* /usr/local/lib/
COPY --from=build /usr/lib/arm-linux-gnueabihf/libprotobuf-c.so* /usr/lib/arm-linux-gnueabihf/
COPY --from=build /usr/lib/arm-linux-gnueabihf/libparson.so* /usr/lib/arm-linux-gnueabihf/
COPY --from=build /usr/lib/arm-linux-gnueabihf/libmosquitto.so* /usr/lib/arm-linux-gnueabihf/
COPY --from=build /usr/lib/arm-linux-gnueabihf/libmx-dx.so* /usr/lib/arm-linux-gnueabihf/
COPY --from=build /usr/local/include/* /usr/local/include/
COPY --from=build /app/app.o /app/run.sh /app/
WORKDIR /app

RUN apt update \
    && apt install -y libmicrohttpd12 libjansson4 libcurl4-gnutls-dev libgnutlsxx28 libgcrypt20 zlib1g-dev libsystemd0

RUN rm /usr/bin/qemu-arm-static

CMD ["./run.sh"]