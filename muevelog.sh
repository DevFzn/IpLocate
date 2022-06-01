#!/usr/bin/env bash

Progrm=$0
VersionStr='2022-05-14'
rutaprgrm=$(dirname $(realpath -s $0))

while read line; do
    declare "$line" 2>/dev/null
done < $rutaprgrm/config.cfg


REd="\e[0;31m";  GRn="\e[0;32m";  BLu="\e[0;34m";
RED="\e[1;31m";  GRN="\e[1;32m";  BLU="\e[1;34m";  
RST="\e[0m";

Err(){
    printf '%bERROR: %s%b\n' "${RED}" "$2" "${RST}" 1>&2
    [ $1 -gt 0 ] && exit $1
}

Info(){
    printf '%bINFO: %s%b\n' "${REd}" "$2" "${RST}" 1>&2
    [ $1 -gt 0 ] && exit $1
}

Uso(){
    while read; do
        printf '%s\n' "$REPLY"
    done <<-EOF
    Ejecuta script del servidor que mueve los logs archivados, copia en ruta
    de trabajo, concatena y elimina los archivos sobrantes.

    Programa pensado para ser llamado por iplocate.py (muevelog.sh --start).

    Operación manual: ./muevelog.sh [OPCION]

    Ruta de trabajo: $destino_log

    Opciones:
      -s, --start                       - Copia, extrae y concatena logs.
      -S, --sync                        - Mueve logs.gz en el servidor (Pre-Copia).
      -C, --copia                       - Copia logs del servidor en ruta de trabajo (Post-sync).
      -x, --extraer                     - Descomprime logs en ruta de trabajo.
      -c, --concat [error.log, all...]  - Concatena logs de la ruta de trabajo.
      -v, --version                     - Muestra la fecha de la versión.
      -h, --help                        - Muestra información de ayuda.
EOF
}

sync_logs(){
    printf '%b   - Sincronizando con %s%b\n' "${GRn}" "${server_name}" "${RST}"
    ssh -M -t $server_name $server_script || Info 1 'No hay logs.gz en este momento'
}

copia_logs(){
    mkdir "$destino_log" 2>/dev/null
    if [[ "$(ls $destino_log/*.* 2>/dev/null)" ]]; then
        Info 0 'Hay logs pendientes de ser cargados a base de datos\n'
    else
        printf '%b   - Moviendo logs.gz%b' "${GRn}" "${RST}"
        rsync --remove-source-files -ha --info=progress2 "${ruta_base}" "${destino_log}"
    fi
}

extrae_logs(){
    if [[ "$(ls $destino_log/*.gz 2>/dev/null)" ]]; then
        for file in $(ls $destino_log/*.gz); do
            gunzip ${file}
        done
    else
        Info 0 'No existen logs.gz para extraer!'
    fi
}

concat_log(){
    log_tipo="${1}"
    if [[ "$(ls $destino_log/$log_tipo.* 2>/dev/null)" ]]; then
        printf '%b   - Concatenando log %s %b' "${GRn}" "${1}" "${RST}"
        for file in $(\ls -v $destino_log/$log_tipo.*); do 
            cat $file >> $destino_log/$log_tipo
            rm -f $file
        done
        printf '%b  ...OK!%b\n' "${GRn}" "${RST}"
    else
        Info 0 "No existen logs [${log_tipo}] para concatenar"
    fi
}

concatena_logs(){
    log_tipos=(access.log error.log reverse-error.log reverse-access.log)
    for tipo in ${log_tipos[@]}; do
        if [[ "$(ls $destino_log/${tipo}.* 2>/dev/null)" ]]; then
            concat_log ${tipo}    
        fi
    done
}

main(){
    printf '%b - Preparación del servidor, pre-copia:%b\n' "${GRN}" "${RST}" &&
    sync_logs || Err 0 'Error al syncronizar!'
    wait
    printf '%b - Copiando logs del servidor en\n   - %s :%b\n' "${GRN}" "${destino_log}" "${RST}" &&
    copia_logs && printf '%b   Copia completada%b\n' "${BLu}" "${RST}" || Err 0 'Error al copiar!'
    wait
    printf '%b - Descomprimiendo archivos gunzip%b\n' "${GRN}" "${RST}" &&
    extrae_logs && printf '%b   Extración completada%b\n' "${BLu}" "${RST}" ||
    Err 0 'Error al descomprimir!'
    wait
    printf '%b - Concatenando archivos:%b\n' "${GRN}" "${RST}" && concatena_logs &&
    printf '%b   Archivos concatenados%b\n\n' "${BLu}" "${RST}" || Err 0 'Error al concatenar logs!'
    #printf '%bProceso terminado %b\n' "${BLU}" "${RST}"
}

if [ -n "${1}" ]; then
    case $1 in
        --sync|-S)
            sync_logs
            exit 0
            ;;
        --copia|-C)
            copia_logs
            exit 0
            ;;
        --extraer|-x)
            extrae_logs
            exit 0
            ;;
        --concat|-c)
            case ${2} in
                access.log)
                    concat_log ${2} ;;
                error.log)
                    concat_log ${2} ;;
                reverse-access.log)
                    concat_log ${2} ;;
                reverse-error.log)
                    concat_log ${2} ;;
                all)
                    concatena_logs ;;
                *)
                    Err 1 'Ingresa el tipo de log a concatenar (access.log, all, etc)' ;;
            esac
            exit 0
            ;;
        --help|-h)
            Uso; exit 0
            ;;
        --version|-v)
            printf '%s\n' "$VersionStr"; exit 0
            ;;
        --help|-h)
            Uso; exit 0
            ;;
        --start|-s)
            main; exit 0
            ;;
        *)
            Err 1 'Argumento(s) invalido(s).' ;;
    esac
else
    Err 1 'Debes incluir una opción. ej: --help'
fi

"$@"
