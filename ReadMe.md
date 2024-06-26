# Getting Started

## Dev Environment Setup (Optional)

In Terminal :

```
$ poetry shell
$ poetry install
```

## OIDC Client Configuration

```
$ cp .env_template .env
```

Populate values for

* client_id=
* client_secret=
* provider_url=

> Ensure your OIDC provider supports standard discovery.


```
$ cat https://cloudsso.cisco.com/.well-known/openid-configuration # For Cisco
```

## Auth Sandbox 

```
$ ./sandbox.bash 
```

## OAuth2 Flow

![alt text](/docs/oauth2-flow.png "OAuth2 Flow")

## Refernces:

[Python Frameworks](https://deepsource.io/blog/new-python-web-frameworks/)