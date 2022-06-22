#include "esp_http_server.h"
#include "main.h"

httpd_handle_t simple_httpd = NULL;


static esp_err_t cmd_handler(httpd_req_t *req){
    char*  buf;
    size_t buf_len;
    char variable[32] = {0,};
    char value[32] = {0,};

    //httpd_resp_set_type(req, "text/html");
    //const char index_html[]="<p>cmd Handler</p>";
    //return httpd_resp_send(req, (const char *)index_html, sizeof(index_html));
    
    buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1) {
        buf = (char*)malloc(buf_len);
        if(!buf){
            httpd_resp_send_500(req);
            return ESP_FAIL;
        }
        if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
            if (httpd_query_key_value(buf, "var", variable, sizeof(variable)) == ESP_OK &&
                httpd_query_key_value(buf, "val", value, sizeof(value)) == ESP_OK) {
            } else {
                free(buf);
                httpd_resp_send_404(req);
                return ESP_FAIL;
            }
        } else {
            free(buf);
            httpd_resp_send_404(req);
            return ESP_FAIL;
        }
        free(buf);
    } else {
        httpd_resp_send_404(req);
        return ESP_FAIL;
    }

    int val = atoi(value);
    int res = 0;

    httpd_resp_set_type(req, "text/html");
    char index_html[512];
    sprintf(index_html,"%s, %d", variable, val);
    return httpd_resp_send(req, (const char *)index_html, sizeof(index_html));


    
    if(!strcmp(variable, "debug")) waterControllerData.debug = val;
    else if(!strcmp(variable, "cycle_secs")) waterControllerData.cycleSecs = val;
    else if(!strcmp(variable, "on_secs")) waterControllerData.onSecs = val;
    else {
        res = -1;
    }

    if(res){
        return httpd_resp_send_500(req);
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, NULL, 0);
}


static esp_err_t index_handler(httpd_req_t *req){
    httpd_resp_set_type(req, "text/html");
    //httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    const char index_html[]="<p>Hello World</p>";
    return httpd_resp_send(req, (const char *)index_html, sizeof(index_html));
}

static esp_err_t status_handler(httpd_req_t *req){
    httpd_resp_set_type(req, "text/html");
    //httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    const char index_html[]="<p>Status Handler</p>";
    return httpd_resp_send(req, (const char *)index_html, sizeof(index_html));
}



void startSimpleServer(){
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();

    httpd_uri_t index_uri = {
        .uri       = "/",
        .method    = HTTP_GET,
        .handler   = index_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t cmd_uri = {
        .uri       = "/control",
        .method    = HTTP_GET,
        .handler   = cmd_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t status_uri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = status_handler,
        .user_ctx  = NULL
    };

    
    Serial.printf("Starting web server on port: '%d'\n", config.server_port);
    if (httpd_start(&simple_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(simple_httpd, &index_uri);
        httpd_register_uri_handler(simple_httpd, &cmd_uri);
        httpd_register_uri_handler(simple_httpd, &status_uri);
    }

}

