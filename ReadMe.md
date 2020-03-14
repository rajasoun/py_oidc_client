# Getting Started

## Dev Environment Setup (Optional)

In Terminal :

```
$ brew install pyenv
$ pyenv install 3.8.2
$ python -m venv .venv
$ source .venv/bin/activate
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
$ cat https://accounts.google.com/.well-known/openid-configuration # For Google:

$ cat https://cloudsso.cisco.com/.well-known/openid-configuration # For Cisco
```

## Docker Compose

```
$ docker-compose -f sso.yml build
$ docker-compose -f sso.yml up
```

## OAuth2 Flow

![alt text](/docs/oauth2-flow.png "OAuth2 Flow")