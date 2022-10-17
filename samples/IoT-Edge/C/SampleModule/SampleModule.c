// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

#include "iothub_module_client.h"
#include "iothub_message.h"
#include "azure_c_shared_utility/threadapi.h"
#include "azure_c_shared_utility/crt_abstractions.h"
#include "azure_c_shared_utility/platform.h"
#include "azure_c_shared_utility/shared_util_options.h"
#include "iothub_client_options.h"
#include "iothubtransportmqtt.h"
#include "iothub.h"
#include "parson.h"
#include "TpeHelper.h"

bool termFlag = false;
static char msgText[1024];
IOTHUB_MODULE_CLIENT_HANDLE iotHubModuleClientHandle;

static void SendConfirmationCallback(IOTHUB_CLIENT_CONFIRMATION_RESULT result, void* userContextCallback)
{
    int count = (int)userContextCallback;
    printf("Message[%d] send completed with result: %s\n", count, MU_ENUM_TO_STRING(IOTHUB_CLIENT_CONFIRMATION_RESULT, result));
    fflush(stdout);
}

static void sendReportedCallback(int status_code, void* userContextCallback)
{
    (void)userContextCallback;
    printf("Twin reported properties update completed with result: %d\n", status_code);
    fflush(stdout);
}

static void connectionStatusCallback(IOTHUB_CLIENT_CONNECTION_STATUS result, IOTHUB_CLIENT_CONNECTION_STATUS_REASON reason, void *userContextCallback)
{
    (void)userContextCallback;
    if (result == IOTHUB_CLIENT_CONNECTION_AUTHENTICATED)
    {
        printf("[Connection Callback] The module is connected.\n");
        fflush(stdout);
    }
    else
    {
        printf("[Connection Callback] The module is disconnected. Status = %s; Reason = %s\n", MU_ENUM_TO_STRING(IOTHUB_CLIENT_CONNECTION_STATUS, result), MU_ENUM_TO_STRING(IOTHUB_CLIENT_CONNECTION_STATUS_REASON, reason));
        fflush(stdout);
    }
}

static void twinCallback(DEVICE_TWIN_UPDATE_STATE update_state, const unsigned char* payLoad, size_t size, void* userContextCallback)
{
    (void)update_state;
    (void)userContextCallback;

    char* twin = (char*)malloc((size + 1) * sizeof(char));
    snprintf(twin, size + 1, "%s", payLoad);
    JSON_Value* root = json_parse_string(twin);
    JSON_Value* desired = NULL;
    if (update_state == DEVICE_TWIN_UPDATE_COMPLETE)
    {
        printf("[Twin Receieved] Twin = %s\n", twin);
        fflush(stdout);
        JSON_Object* rootObj = json_value_get_object(root);
        if (json_object_has_value(rootObj, "desired"))
        {
            desired = json_object_get_value(rootObj, "desired");
            char* desiredString = json_serialize_to_string_pretty(desired);
            printf("[Twin Receieved] Desired = %s\n", desiredString);
            fflush(stdout);
            json_free_serialized_string(desiredString);
        }
    }
    else
    {
        printf("[Twin Receieved] Desired = %s\n", twin);
        fflush(stdout);
        desired = root;
    }

    if (desired)
    {
        JSON_Object* desiredObj = json_value_get_object(desired);
        if (json_object_has_value(desiredObj, "$version"))
        {
            if (json_object_remove(desiredObj, "$version") != JSONSuccess)
            {
                printf("[Twin Receieved] Failed to remove version info.\n");
                fflush(stdout);
            }
        }
        char* reportedProperties = json_serialize_to_string(desired);
        printf("[Twin Receieved] Updating reported properties = %s\n", reportedProperties);
        fflush(stdout);
        (void)IoTHubModuleClient_SendReportedState(iotHubModuleClientHandle, (const unsigned char*)reportedProperties, strlen(reportedProperties), sendReportedCallback, NULL);
        json_free_serialized_string(reportedProperties);
    }
    json_value_free(root);
    free(twin);
}

static int methodCallback(const char* method_name, const unsigned char* payload, size_t size, unsigned char** response, size_t* response_size, void* userContextCallback)
{
    (void)userContextCallback;
    (void)payload;
    (void)size;

    char* payloadString = (char*)malloc((size + 1) * sizeof(char));
    snprintf(payloadString, size + 1, "%s", payload);
    printf("[Direct Method Receieved]\nMethod Name = %s\nPayload = %s\n", method_name, payloadString);
    fflush(stdout);

    int result;
    if (strcmp("thingspro_api_v1", method_name) == 0)
    {

        JSON_Value* root = json_parse_string(payload);
        if (!root)
        {
            printf("ERROR: payload must be in JSON format.\n");
            fflush(stdout);
            free(payloadString);
            return -1;
        }
        JSON_Object* rootObj = json_value_get_object(root);
        const char* path = json_object_get_string(rootObj, "path");
        const char* method = json_object_get_string(rootObj, "method");
        char* requestBody = NULL;
        if (json_object_has_value_of_type(rootObj, "requestBody", JSONObject))
        {
            JSON_Value* request = json_object_get_value(rootObj, "requestBody");
            char *requestString = json_serialize_to_string(request);
            requestBody = (char*)malloc((strlen(requestString) + 1) * sizeof(char));
            snprintf(requestBody, strlen(requestString) + 1, "%s", requestString);
            json_free_serialized_string(requestString);
        }
        else if (json_object_has_value_of_type(rootObj, "requestBody", JSONString))
        {
            const char* request = json_object_get_string(rootObj, "requestBody");
            requestBody = (char*)malloc((strlen(request) + 1) * sizeof(char));
            snprintf(requestBody, strlen(request) + 1, "%s", request);
        }

        if (!path || !method || !requestBody)
        {
            printf("ERROR: Missing required field(s).\n");
            fflush(stdout);
            free(payloadString);
            return -1;
        }

        char *apiResponse = NULL;
        result = tpe_invokeApi((char*)method, (char*)path, requestBody, false, &apiResponse);
        *response_size = strlen(apiResponse);
        *response = (unsigned char*)malloc((*response_size) * sizeof(char));
        (void)memcpy(*response, apiResponse, *response_size);
        free(apiResponse);
    }
    else
    {
        const char methodResponse[] = "{\"message\": \"Error: The method name is not supported.\"}";
        *response_size = sizeof(methodResponse) - 1;
        *response = malloc(*response_size);
        (void)memcpy(*response, methodResponse, *response_size);
        result = 404;
    }
    free(payloadString);
    return result;
}

static IOTHUBMESSAGE_DISPOSITION_RESULT messageCallback(IOTHUB_MESSAGE_HANDLE message, void *userContextCallback)
{
    (void)userContextCallback;
    IOTHUBMESSAGE_CONTENT_TYPE content_type = IoTHubMessage_GetContentType(message);
    if (content_type == IOTHUBMESSAGE_BYTEARRAY)
    {
        const unsigned char* buff_msg;
        size_t buff_len;

        if (IoTHubMessage_GetByteArray(message, &buff_msg, &buff_len) != IOTHUB_MESSAGE_OK)
        {
            printf("[Message Received]\nFailure retrieving byte array message\n");
            fflush(stdout);
        }
        else
        {
            char* payload = (char*)malloc((buff_len + 1) * sizeof(char));
            snprintf(payload, buff_len + 1, "%s", buff_msg);
            const char* topic = IoTHubMessage_GetInputName(message);
            MAP_HANDLE properties = IoTHubMessage_Properties(message);
            (void)printf("[Message Received]\nTopic = %s\nPayload = %s\n", topic, payload);
            fflush(stdout);
            free(payload);
        }
    }
    else
    {
        const char* string_msg = IoTHubMessage_GetString(message);
        if (string_msg == NULL)
        {
            printf("[Message Receieved]\nFailure retrieving string message\n");
            fflush(stdout);
        }
        else
        {
            const char* topic = IoTHubMessage_GetInputName(message);
            MAP_HANDLE properties = IoTHubMessage_Properties(message);
            printf("[Message Received]\nTopic = %s\nPayload = %s\n", topic, string_msg);
            fflush(stdout);
        }
    }
    return IOTHUBMESSAGE_ACCEPTED;
}

static void signalHandler(int signal_number)
{
    termFlag = true;
}

int main(void)
{
    struct sigaction act;
    memset(&act, 0, sizeof(act));
    act.sa_handler = &signalHandler;
    sigaction(SIGINT, &act, NULL);
    sigaction(SIGKILL, &act, NULL);
    sigaction(SIGTERM, &act, NULL);

    IOTHUB_MESSAGE_HANDLE message_handle;

    srand((unsigned int)time(NULL));

    if (IoTHub_Init() != 0)
    {
        printf("ERROR: Failed to initialize the platform.\n");
        fflush(stdout);
        return -1;
    }
    // Note: You must use MQTT_Protocol as the argument below.  Using other protocols will result in undefined behavior.
    else if ((iotHubModuleClientHandle = IoTHubModuleClient_CreateFromEnvironment(MQTT_Protocol)) == NULL)
    {
        printf("ERROR: iotHubModuleClientHandle is NULL!\n");
        fflush(stdout);
        IoTHub_Deinit();
    }
    else
    {
        // Uncomment the following lines to enable verbose logging (e.g., for debugging).
        // bool traceOn = true;
        // IoTHubModuleClient_LL_SetOption(iotHubModuleClientHandle, OPTION_LOG_TRACE, &traceOn);a

        //Setting the auto URL Encoder (recommended for MQTT). Please use this option unless
        //you are URL Encoding inputs yourself.
        //ONLY valid for use with MQTT
        bool urlEncodeOn = true;
        (void)IoTHubModuleClient_SetOption(iotHubModuleClientHandle, OPTION_AUTO_URL_ENCODE_DECODE, &urlEncodeOn);

        (void)IoTHubModuleClient_SetConnectionStatusCallback(iotHubModuleClientHandle, connectionStatusCallback, NULL);
        (void)IoTHubModuleClient_SetModuleMethodCallback(iotHubModuleClientHandle, methodCallback, NULL);
        (void)IoTHubModuleClient_SetModuleTwinCallback(iotHubModuleClientHandle, twinCallback, NULL);
        (void)IoTHubModuleClient_SetMessageCallback(iotHubModuleClientHandle, messageCallback, NULL);

        if(tpe_init())
        {
            printf("ERROR: Failed to initialize TPE helper.\n");
        }

        int count = 0;
        int interval = 30;
        while (1)
        {
            if (termFlag) {
                printf("Signal captured, terminating...\n");
                fflush(stdout);
                tpe_uninit();
                IoTHub_Deinit();
                IoTHubModuleClient_Destroy(iotHubModuleClientHandle);
                break;
            }
            sprintf_s(msgText, sizeof(msgText), "{\"value\":%d}", count);
            IOTHUB_MESSAGE_HANDLE message_handle = IoTHubMessage_CreateFromString(msgText);
            if (message_handle == NULL)
            {
                printf("ERROR: iotHubMessageHandle is NULL!\n");
                fflush(stdout);
            }
            else
            {
                (void)IoTHubMessage_SetContentTypeSystemProperty(message_handle, "application%2fjson");
                (void)IoTHubMessage_SetContentEncodingSystemProperty(message_handle, "utf-8");

                (void)IoTHubMessage_SetProperty(message_handle, "property_key", "property_value");

                if (IoTHubModuleClient_SendEventToOutputAsync(iotHubModuleClientHandle, message_handle, "Output", SendConfirmationCallback, (void*)count) != IOTHUB_CLIENT_OK)
                {
                    printf("ERROR: IoTHubModuleClient_LL_SendEventAsync..........FAILED!\n");
                    fflush(stdout);
                }
                else
                {
                    printf("IoTHubModuleClient_SendEventToOutputAsync accepted message [%d] for transmission to IoT Hub.\n", count);
                    fflush(stdout);
                }
            }
            IoTHubMessage_Destroy(message_handle);
            if (count < 86400 / interval)
                ++count;
            else
                count = 0;
            ThreadAPI_Sleep(interval * 1000);
        }
    }
}
