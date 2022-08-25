#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <unistd.h>
#include <curl/curl.h>
#include <stdbool.h>
#include <signal.h>
#include <libmx-dx/dx_api.h>
#include <libmx-dx/dx_value.h>
#include <ulfius.h>
#include <jansson.h>

#define PORT 80

bool termFlag = false;

/**
 * Callback function for the web application on /helloworld url call
 */
int callback_hello_world (const struct _u_request * request, struct _u_response * response, void * user_data) {
    ulfius_set_string_body_response(response, 200, "Hello!");
    return U_CALLBACK_CONTINUE;
}

void dx_callback(DX_TAG_OBJ *dx_tag_obj, uint16_t obj_cnt, void *user_data)
{
    int i = 0;
    printf("Tag: %s, ", dx_tag_obj[0].tag);
    printf("Value type: ");
    switch(dx_tag_obj[0].val_type) {
    case DX_TAG_VALUE_TYPE_INT8:
        printf("int8, Value: %d, ", dx_tag_obj[0].val.i8);
        break;
    case DX_TAG_VALUE_TYPE_INT16:
        printf("int16, Value: %d, ", dx_tag_obj[0].val.i16);
        break;
    case DX_TAG_VALUE_TYPE_INT32:
        printf("int32, Value: %d, ", dx_tag_obj[0].val.i32);
        break;
    case DX_TAG_VALUE_TYPE_INT64:
        printf("int64, Value: %"PRId64", ", dx_tag_obj[0].val.i64);
        break;
    case DX_TAG_VALUE_TYPE_INT: // deprecated
        printf("int8, Value: %"PRId64", ", dx_tag_obj[0].val.i);
        break;
    case DX_TAG_VALUE_TYPE_UINT8:
        printf("uint8, Value: %u, ", dx_tag_obj[0].val.u8);
        break;
    case DX_TAG_VALUE_TYPE_UINT16:
        printf("uint16, Value: %u, ", dx_tag_obj[0].val.u16);
        break;
    case DX_TAG_VALUE_TYPE_UINT32:
        printf("uint32, Value: %u, ", dx_tag_obj[0].val.u32);
        break;
    case DX_TAG_VALUE_TYPE_UINT64:
        printf("uint64, Value: %"PRIu64", ", dx_tag_obj[0].val.u64);
        break;
    case DX_TAG_VALUE_TYPE_UINT: // deprecated
        printf("uint, Value: %"PRIu64", ", dx_tag_obj[0].val.u);
        break;
    case DX_TAG_VALUE_TYPE_FLOAT:
        printf("float, Value: %f, ", dx_tag_obj[0].val.f);
        break;
    case DX_TAG_VALUE_TYPE_DOUBLE:
        printf("double, Value: %lf, ", dx_tag_obj[0].val.d);
        break;
    case DX_TAG_VALUE_TYPE_STRING:
        printf("string, Value: %s, ", dx_tag_obj[0].val.s);
        break;
    case DX_TAG_VALUE_TYPE_BYTEARRAY:
        printf("bytearray, Value:");
        for (; i < dx_tag_obj[0].val.bl; i++) {
            printf(" %02X", dx_tag_obj[0].val.b[i]);
        }
        printf(", ");
        break;
    case DX_TAG_VALUE_TYPE_RAW:
        printf("Value type: raw, Value:");
        for (; i < dx_tag_obj[0].val.rl; i++) {
            printf(" %02X", dx_tag_obj[0].val.rp[i]);
        }
        printf(", ");
        break;
    default:
        break;
    }
    printf("AtMs: %"PRId64"\n", dx_tag_obj[0].timestamp);
}

struct memory {
    char *response;
    size_t size;
};

size_t write_callback(char *data, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct memory *mem = (struct memory *)userp;

    char *ptr = realloc(mem->response, mem->size + realsize + 1);
    if (ptr == NULL)
        return 0;

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), data, realsize);
    mem->size += realsize;
    mem->response[mem->size] = 0;
    return realsize;
}

static void signalHandler(int signal_number)
{
    termFlag = true;
}

void init()
{
    struct sigaction act;
    memset(&act, 0, sizeof(act));
    act.sa_handler = &signalHandler;
    sigaction(SIGINT, &act, NULL);
    sigaction(SIGKILL, &act, NULL);
    sigaction(SIGTERM, &act, NULL);

    CURLcode res;
    res = curl_global_init(CURL_GLOBAL_DEFAULT);
    /* Check for errors */
    if(res != CURLE_OK) {
        printf("Error: curl_global_init() failed: %s\n", curl_easy_strerror(res));
        return;
    }
}

void uninit()
{
    curl_global_cleanup();
}

void manage_tag(bool register_tag)
{
    CURL *curl;
    CURLcode res;

    const char *host_ip = getenv("APPMAN_HOST_IP");
    if (!host_ip) {
        printf("Error: Failed to get docker network gateway's IP, skipping.\n");
        return;
    }

    curl = curl_easy_init();
    if(curl) {
        struct memory chunk;
        char *url = (char *)malloc((strlen(host_ip) + 33 + 1) * sizeof(char));
        snprintf(url, strlen(host_ip) + 33 + 1, "http://%s:59000/api/v1/tags/virtual", host_ip);
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

        // printf("url = %s\n", url);

        // token
        char *token = NULL;
        FILE *fp = fopen("/var/run/mx-api-token", "r");
        if (fp)
        {
            // get file size
            fseek(fp, 0, SEEK_END);
            long fSize = ftell(fp);
            rewind(fp);

            token = (char *)malloc(((size_t)fSize + 1) * sizeof(char));
            fread(token, 1, fSize, fp);
            fclose(fp);
            token[fSize] = '\0';
        }

        // printf("token = %s\n", token);

        // header
        struct curl_slist *curlList = NULL;
        curlList = curl_slist_append(curlList, "Content-Type: application/json");
        char authHeader[4096];
        snprintf(authHeader, 4096, "Authorization: Bearer %s", token);
        curlList = curl_slist_append(curlList, authHeader);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, curlList);
        free(token);

        chunk.response = malloc(1);
        chunk.size = 0;

        // payload
        char *payload = NULL;
        json_t *root = json_object();
        json_object_set_new(root, "prvdName", json_string("application"));
        json_object_set_new(root, "srcName", json_string("hello"));
        json_object_set_new(root, "tagName", json_string("output1"));
        if (register_tag) {
            json_object_set_new(root, "dataType", json_string("int32"));
            json_object_set_new(root, "access", json_string("rw"));
        }
        payload = json_dumps(root, 0);

        // printf("payload = %s\n", payload);

        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload);
        if (!register_tag)
            curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");

        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            printf("curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        long retCode = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &retCode);
        if (retCode != 200) {
            printf("Curl Return Code is not 200: %d\n", retCode);
            printf("%s\n", chunk.response);
        }
        free(chunk.response);
        free(payload);
        json_decref(root);
        free(url);

        curl_slist_free_all(curlList);
        curl_easy_cleanup(curl);
    }
}

DX_TAG_CLIENT *tpe_init()
{
    DX_TAG_CLIENT *client = dx_tag_client_init("hello", dx_callback);
    if (client == NULL) {
        return NULL;
    }
    if (dx_tag_sub(client, "+/+/+", NULL)) {
        printf("subscribe all failed\n");
    }
    return client;
}

/**
 * main function
 */
int main(void) {

    init();

    struct _u_instance instance;

    // Initialize ulfius instance with the port number
    if (ulfius_init_instance(&instance, PORT, NULL, NULL) != U_OK) {
        fprintf(stderr, "Error ulfius_init_instance, abort\n");
        return(1);
    }

    // Endpoint list declaration
    ulfius_add_endpoint_by_val(&instance, "GET", "/api/v1/hello", NULL, 0, &callback_hello_world, NULL);

    // Start ulfius framework
    if (ulfius_start_framework(&instance) == U_OK) {
        printf("Start framework on port %d\n", instance.port);
    }
    else {
        fprintf(stderr, "Error starting framework\n");
    }

    manage_tag(true);
    DX_TAG_CLIENT *client = tpe_init();

    DX_TAG_VALUE value;
    value.i32 = 0;
    while(1) {
        if (termFlag) {
            printf("Signal captured, terminating...\n");
            manage_tag(false);
            uninit();
            break;
        }

        printf("Publishing value: %d\n", value.i32);

        // To be fixed: the latest tag SDK cannot publish tag successfully
        int rc = dx_tag_pub(
                client,
                "application/hello/output1",
                DX_TAG_VALUE_TYPE_INT32,
                value,
                0);

        if (rc != DX_TAG_OK)
            printf("publish failed (%d)\n", rc);

        if (value.i32 <= 8640)
            value.i32 += 1;
        else
            value.i32 = 0;

        sleep(10);
    }

    printf("End framework\n");

    ulfius_stop_framework(&instance);
    ulfius_clean_instance(&instance);

    return 0;
}
