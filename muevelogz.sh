#!/usr/bin/env bash

# Permitir al usuario correr este script como super
# usuario sin solicitar contraseña, agregandolo al
# archivo sudoers

serv_user=<nombre_usuario>
# logdest debe ser la misma ruta especificada en config.cfg como *ruta_base*
logdest=/home/$serv_user/nginx_log.old
logdir=/var/log/nginx

mkdir $logdest 2>/dev/null

mueve_loggz(){
    if [[ "$(ls $logdir/*.log.*.gz 2>/dev/null)" ]]; then
        printf 'Moviendo logs.gz de %s/\n' "${logdir}"
        mv $logdir/*.log.*.gz $logdest
        chown $serv_user:$serv_user $logdest/*
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
