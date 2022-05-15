# iplocate

## Gestión de logs *nginx* archivados

Mueve archivos ***log.?.gz*** del servidor existentes en `/var/log/nginx` al directorio  
de usuario "**ruta_base**" en el servidor especificado en `./config.cfg`. Utiliza el  
script `muevelogz.sh` (script en servidor).  

Mueve los archivos ***log.?.gz*** del directorio de usuario del servidor al directorio  
local "**destino_log**" especificado en `./config.cfg`.  
Descomprime archivos **`.gz`** y concatena los respectivos archivos de log.  
Borra los archivos utilizados en concatenación. Script `./muevelog.sh`.  

ej. archivo de configuración `./config.cfg`
```cfg
[bash_script]
ruta_base=mi_server://home/server_user/nginx_log.old/
destino_log=/home/server_logs/nginx_old
server_name=mi_server
server_script=//home/server_user/scripts/muevelogz.sh

[iplocate]
token = '?token=1234567890abc'
```
- ***mi_server***: parte de *ruta_base*, nombre del host según configuración  
  en `~/.ssh/config`.  
- **ruta_base** : es la ruta en el servidor donde se mueven los logs  
  archivados (.gz) desde `/var/log/nginx/` (termina en `/`).  
- **destino_log** : ruta donde se guardan local y temporalmente los  
  archivos *log.?.gz*.  
- **server_name** : nombre del host según configuración en `~/.ssh/config`.  
- **server_script** : ruta en el servidor, del script que mueve los *log.?.gz*.


Crea base de datos ***SQLite3*** **`./ipinfo.db`** con tablas de **registro** y de **visitas**.  

## Uso
`./iplocate.py -h`  
ej. alias `alias iploc='~/ruta/script/iplocate.py'`  
```bash
    ipLocate
        Muestra información disponible en ipinfo.io sobre IPs consultadas.

    Uso:
        iploc <IP>             - Consulta la información de <IP> disponible en ipinfo.io.
        iploc -t <IP>          - Consulta la info. de <IP> usando 'token' de ipinfo.io, 
                                 especificado en config.cfg.
        iploc -f <archivo>     - Consulta info. de las IPs en <archivo> (ipinfo.ip).
        iploc -D <archivo>     - Consulta info. de las IPs en <archivo> (base de datos).
        iploc -d <IP>          - Muestra toda la info. disponible de <IP> registrada en BD.
        iploc -c               - Carga logs en base de datos.
        iploc -g               - Guarda ipinfo de IPs sin registro en la BD.
        iploc -h               - Muestra esta ayuda.
        iploc --sync           - Sincroniza logs del servidor (bash script).

```

**`iploc --sync`**  
Realiza el proceso de copia de archivos del servidor, extracción y concatenado.  
Explicado con detalle mas arriba.  

**`iploc -c`**  
Poblar la tabla **visita** de la BD. Carga los registros en archivos de log en la tabla.  

**`iploc -g`**  
Consulta a `ipinfo.io` por cada ip registrada en **visita** (una vez por ip).  
Guarda los datos en tabla **registro**.

### Otras opciones

`iploc <IP>`:  
  - Muestra la información sobre \<IP\> disponible en ipinfo.io.  

`iploc -t <IP>`: **PENDIENTE**  
  - Muestra la información sobre \<IP\> disponible en ipinfo.io  
  usando el **token** especificado en `./config.cfg`.  

`iploc -d <IP>`: **PENDIENTE**  
  - Muestra toda la información disponible en BD acerca de \<IP\>  

`iploc -f <archivo_IPs>`:  
  - Muestra la información disponible en ipinfo.io para cada \<IP\>  
  en archivo pasado como argumento.  

`iploc -D <archivo_IPs>`: **PENDIENTE**  
  - Muestra toda la información disponible en BD para cada \<IP\>  
  en archivo pasado como argumento.  

ej. formato \<archivo_IPs\>.  
```
1.1.1.1
8.8.8.8
...
```  

### Sicronización manual

No es necesario el uso manual de este script, ya que es llamado por `iploc --sync`.  
Pero ya que existe por que no tener la opción de llamar manualmente a las funciones.  

`./muevelog.sh -h`  
```
    Ejecuta script del servidor que mueve los logs archivados, copia en ruta
    de trabajo, concatena y elimina los archivos sobrantes.

    Programa pensado para ser llamado por iplocate.py (muevelog.sh --start).

    Operación manual: ./muevelog.sh [OPCION]

    Ruta de trabajo: </ruta/segun/config.cfg>

    Opciones:
      -s, --start                       - Copia, extrae y concatena logs.
      -S, --sync                        - Mueve logs.gz en el servidor (Pre-Copia).
      -C, --copia                       - Copia logs del servidor en ruta de trabajo (Post-sync).
      -x, --extraer                     - Descomprime logs en ruta de trabajo.
      -c, --concat [error.log, all...]  - Concatena logs de la ruta de trabajo.
      -v, --version                     - Muestra la fecha de la versión.
      -h, --help                        - Muestra información de ayuda.
```

`./muevelog.sh --start`:  
Realiza todo el proceso **--sync**,  **--copia**, **--extraer** y **--concat**.  


### Implementación
Clonar proyecto en directorio ej. `~/nginx_data`.  

Crear `alias iploc='~/nginx_data/iplocate.py'`.  

Modificar ruta **logdest** en `muevelogz.sh` y copiar en el servidor.  
```
# logdest debe ser la misma ruta especificada en config.cfg como *ruta_base*
logdest=</ruta/user/docs/logs/nginx_log.old>
```
Crear archivo de configuración según ejemplo mostrado en la primera sección  
de este documento.  

Correr `iploc -h` para crear base de datos.  

```
📂️ nginx_data/
├── 📄️ config.cfg
├── 📄️ ipinfo.db
├── 📄️ iplocate.py
├── 📄️ muevelog.sh
├── 📄️ muevelogz.sh
├── 📄️ README.md
└── 📄️ sql_alch.py
```

Seguir los pasos explicados en  **Uso**.

### Requerimientos, dependencias

Servidor:
- Bash >= 5.0
- rsync  

Local:
- Bash local >= 5.1.16
- SQLite3 3.38.5
- sqlitebrowser 3.35.5 (opc.)
- Python >= 3.10
  - requests
  - SQLAlchemy 1.4.32
  - colorama

Token API [ipinfo.io](https://ipinfo.io/)


