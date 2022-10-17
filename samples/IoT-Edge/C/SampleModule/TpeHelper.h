int tpe_init();
void tpe_uninit();
int tpe_invokeApi(char* method, char* endPoint, char* payload, bool isStream, char** response);
