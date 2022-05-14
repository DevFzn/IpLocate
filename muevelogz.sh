#!/usr/bin/env bash

# logdest debe ser la misma ruta especificada en config.cfg como *ruta_base*
logdest=</ruta/user/docs/logs/nginx_log.old>
serv_user="${USER}"

logdir=/var/log/nginx

mueve_loggz(){
    if [[ "$(ls $logdir/*.log.*.gz 2>/dev/null)" ]]; then
        printf 'Moviendo logs.gz de %s/\n' "${logdir}"
        sudo mv $logdir/*.log.*.gz $logdest
        sudo chown $serv_user:$serv_user $logdest/*
    else
        printf 'No hay logs archivados para mover\n'
        exit 1
    fi
    exit 0
}

if [[ "$(ls $logdest/*.gz 2>/dev/null)" ]]; then
    printf 'Existen logs pendientes de respaldo\n'
else
    mueve_loggz
fi
exit 0
