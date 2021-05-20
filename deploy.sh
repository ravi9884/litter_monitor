#!/bin/bash
docker-compose push
docker stack deploy --compose-file docker-compose.yml litter-monitor
docker service logs -f litter-monitor_litter-monitor 