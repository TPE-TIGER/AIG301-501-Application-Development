#! /bin/bash

gcc SampleModule.c TpeHelper.c -o out \
    -DUSE_EDGE_MODULES -DUSE_PROV_MODULE \
    -I azure-iot-sdk-c/iothub_client/inc/ \
    -I azure-iot-sdk-c/deps/umock-c/inc/ \
    -I azure-iot-sdk-c/deps/azure-macro-utils-c/inc/ \
    -I azure-iot-sdk-c/deps/parson \
    -I azure-iot-sdk-c/c-utility/inc/ \
    -L azure-iot-sdk-c/cmake/iothub_client/ \
    -L azure-iot-sdk-c/cmake/provisioning_client/deps/utpm/ \
    -L azure-iot-sdk-c/cmake/provisioning_client/ \
    -L azure-iot-sdk-c/cmake/deps/parson/ \
    -L azure-iot-sdk-c/cmake/deps/uhttp/ \
    -L azure-iot-sdk-c/cmake/umqtt/ \
    -L azure-iot-sdk-c/cmake/c-utility/ \
    -lpthread -lssl -lcrypto -lcurl -lm -luuid -ldl \
    -liothub_client \
    -liothub_client_mqtt_transport \
    -lprov_auth_client \
    -lhsm_security_client \
    -lutpm \
    -lparson \
    -lumqtt \
    -luhttp \
    -laziotsharedutil
