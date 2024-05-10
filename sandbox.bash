#!/usr/bin/env bash

set -eo pipefail

COMPOSE_FILES=" -f docker-compose.yml"

function help(){
    echo "Usage: $0  {up|down|status|logs}" >&2
    echo
    echo "   up               Provision, Configure, Validate Application Stack"
    echo "   down             Destroy Application Stack"
    echo "   status           Displays Status of Application Stack"
    echo "   logs             Application Stack Logs"
    echo
    return 1
}

function wait-for-url() {
    echo "Testing $1"
    timeout -s TERM 10 bash -c \
    'while [[ "$(curl -s -o /dev/null -L -w ''%{http_code}'' ${0})" != "200" ]];\
    do echo "Waiting for ${0}" && sleep 2;\
    done' ${1}
    echo "OK!"
    curl -I $1
}


function url_check() {
    HOST=$1
    echo "URL Status Check "
    if curl -s --head  --request GET $HOST | grep "200 OK" > /dev/null; then 
      echo "$HOST  -> UP"
    else
      echo "$HOST  -> DOWN"
    fi
}

opt="$1"
choice=$( tr '[:upper:]' '[:lower:]' <<<"$opt" )
case $choice in
    up)
      echo "Bring Up Auth Application Stack"
      # docker run -d --name="cli-logs" --rm \
      #        --volume=/var/run/docker.sock:/var/run/docker.sock \
      #        --publish=127.0.0.1:8989:80 gliderlabs/logspout
      docker-compose ${COMPOSE_FILES} up --build -d
      wait-for-url "http://localhost:3000" 
      url_check "http://localhost:3000" 
      echo -e "Goto Auth -> http://localhost:3000"
      ;;
    down)
      echo "Destroy Application Stack & Services"
      docker-compose ${COMPOSE_FILES} down -v --remove-orphans
      docker stop cli-logs
      ;;
    status)
      echo -e "\nContainers Status..."
      url_check "http://localhost:3000" 
      docker-compose ${COMPOSE_FILES}  ps
      ;;
    logs)
      echo "Containers Log..."
      # curl http://127.0.0.1:8989/logs
      docker-compose ${COMPOSE_FILES}  logs -f
      ;;
    *)  help ;;
esac