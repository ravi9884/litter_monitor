#!/bin/bash
trap 'exit -1' ERR
docker-compose build 
#--no-cache
docker-compose up -d
docker logs -f litter-monitor