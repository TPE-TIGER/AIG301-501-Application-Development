#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <curl/curl.h>

static char* host = "172.31.8.1";
char* token = NULL;

struct MemoryStruct
{
    char* memory;
    size_t size;
};

size_t WriteMemoryCallback(void* contents, size_t size, size_t nmemb, void* userp)
{
    size_t realsize = size * nmemb;
    struct MemoryStruct* mem = (struct MemoryStruct*)userp;

    mem->memory = (char*)realloc(mem->memory, mem->size + realsize + 1);
    if (mem->memory == NULL)
    {
        /* out of memory! */
        printf("ERROR: Not enough memory (realloc returned NULL).\n");
        fflush(stdout);
        return 0;
    }

    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
};

int tpe_init()
{
    // Load token
    FILE *fp = fopen("/run/mx-api-token", "r");
    if (!fp)
    {
        printf("ERROR: Failed to load API token.\n");
        fflush(stdout);
        return -1;
    }
    // get file size
    fseek(fp, 0, SEEK_END);
    long fSize = ftell(fp);
    rewind(fp);

    token = (char *)malloc(((size_t)fSize + 1) * sizeof(char));
    fread(token, 1, fSize, fp);
    fclose(fp);
    token[fSize] = '\0';
    return curl_global_init(CURL_GLOBAL_DEFAULT);
}

void tpe_uninit()
{
    free(token);
    curl_global_cleanup();
}

int tpe_invokeApi(char* method, char* endPoint, char* payload, bool isStream, char** response)
{
    char url[1024];
    snprintf(url, 1024, "http://%s:59000/api/v1%s", host, endPoint);
    CURLcode *curl = curl_easy_init();
    if (curl)
    {
        curl_easy_setopt(curl, CURLOPT_URL, url);

        struct curl_slist *list = NULL;
        list = curl_slist_append(list, "Content-Type:application/json");
        char authHeader[4096];
        snprintf(authHeader, 4096, "Authorization: Bearer %s", token);
        list = curl_slist_append(list, authHeader);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, list);

        struct MemoryStruct chunk;
        chunk.memory = (char*)malloc(1);
        chunk.memory[0] = '\0';
        chunk.size = 0;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*)&chunk);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);

        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, method);
        if (payload)
        {
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload);
            curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, strlen(payload));
        }

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK)
        {
            printf("ERROR: curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            fflush(stdout);
            curl_slist_free_all(list);
            free(chunk.memory);
            curl_easy_cleanup(curl);
            return -1;
        }
        else
        {
            *response = (char*)malloc((strlen(chunk.memory) + 1) * sizeof(char));
            snprintf(*response, strlen(chunk.memory) + 1, "%s", chunk.memory);
        }

        long http_code = 0;
        curl_easy_getinfo (curl, CURLINFO_RESPONSE_CODE, &http_code);

        printf("[API Result] %d, %s\n", http_code, chunk.memory);
        fflush(stdout);

        curl_slist_free_all(list);
        free(chunk.memory);
        curl_easy_cleanup(curl);
        return (int)http_code;
    }
    else
    {
        printf("ERROR: curl_easy_init() failed.\n");
        fflush(stdout);
        return -1;
    }
}
