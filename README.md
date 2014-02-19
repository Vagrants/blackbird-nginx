blackbird-nginx
===============

[![Build Status](https://travis-ci.org/Vagrants/blackbird-nginx.png?branch=development)](https://travis-ci.org/Vagrants/blackbird-nginx)

Get status by using "GET /stub_status"

config file
-----------

| name                    | default        | type                | notes                               |
|-------------------------|----------------|---------------------|-------------------------------------|
| host                    | 127.0.0.1      | string              | nginx host                          |
| port                    | 80             | interger(1 - 65535) | nginx lisetn port                   |
| timeout                 | 3              | interger(0 - 600)   | timeout for connection              |
| status_uri              | /nginx_status  | string              | stub sttaus uri                     |
| user                    | None           | string              | username for basic authentication   |
| password                | None           | string              | password for basic authentication   |
| ssl                     | False          | boolean             | use ssl for connection              |
| response_check_host     | 127.0.0.1      | string              | nginx host for L7 response check    |
| response_check_port     | 80             | interger(1 - 65535) | nginx port for L7 response check    |
| response_check_timeout  | 3              | interger(0 - 600)   | timeout for L7 response check       |
| response_check_vhost    | localhost      | string              | nginx vhost for L7 response check   |
| response_check_uagent   | blackbird response check | string    | user agent for L7 response check    |
| response_check_ssl      | False          | boolean             | use ssl for L7 response check       |
| path                    | /usr/sbin/nginx| string              | "nginx -v" for version detect       |


Please see the "nginx.cfg"
