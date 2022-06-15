## Gestión de logs *nginx* archivados

- Consulta información sobre IP(s) disponibles en ipinfo.io con o sin token.  

- Mueve archivos ***log.?.gz*** del servidor existentes en `/var/log/nginx` al directorio  
de usuario **"ruta_base"** en el servidor especificado en `./config.cfg`. Utiliza el  
script `muevelogz.sh` (script en servidor).  

- Mueve los archivos ***log.?.gz*** del directorio de usuario del servidor al directorio  
local **"destino_log"** especificado en `./config.cfg`.  

- Descomprime archivos **`.gz`** y concatena los respectivos archivos de log.  
Borra los archivos utilizados en concatenación. Script `./muevelog.sh`.  

- Crea base de datos ***SQLite3*** **`./ipinfo.db`** con tablas de **registro** y de **visitas**.  

- Carga logs archivados de nginx en base de datos.  

- Consulta con ipinfo.io y registra en base de datos.

- Consultas y reportes según información en la base de datos.  


## Uso

ej. alias `alias iploc='~/ruta/script/iplocate.py'`  
`iploc -h`  
```bash
  ipLocate

      Consulta información sobre IP(s) disponibles en ipinfo.io con o sin token.
      Carga logs de nginx en base de datos. Consulta con ipinfo.io y registra
      en base de datos.
      Consultas y reportes según información en la base de datos.

      iploc -h              - Muestra esta ayuda.

  Consultas ipinfo.io:
      iploc <IP>            - Consulta la información de <IP> disponible en ipinfo.io.
      iploc -f <archivo>    - Consulta info. de las IPs en <archivo> (ipinfo.io).
      iploc -t <IP>         - Consulta la info. de <IP> usando 'token' de ipinfo.io,
                              especificado en config.cfg.
      iploc -F <archivo>    - Consulta info. de las IPs en <archivo> (token ipinfo.io).

  Consultas base de datos:
      iploc -d <IP>         - Consulta la información de <IP> disponible en base de datos.
      iploc -D <archivo>    - Consulta info. de las IPs en <archivo> (base de datos).
      iploc -M              - Genera mapa según registro de la BD (cod. 200 y otros).

  Operaciones base de datos:
      iploc --sync          - Sincroniza logs del servidor (bash script).
      iploc -c              - Carga logs en base de datos.
      iploc -g              - Guarda ipinfo de IPs sin registro en la BD.
      iploc --all           - Realiza las 3 operaciones para poblar BD (--sync, -c y -g) y -M.
```

**`iploc --sync`**  
Realiza el proceso de copia de archivos del servidor, extracción y concatenado.  
Explicado al comienzo de este documento.  

**`iploc -c`**  
Poblar tabla **visita** de la base de datos. Carga los registros en archivos de log en la tabla.  

**`iploc -g`**  
Consulta a `ipinfo.io` por cada ip registrada en **visita** (una vez por ip).  
Guarda los datos en tabla **registro**.

**`iploc -M`**  
Genera mapas según vistas registradas. Visitas *infructuosas* de color rojo. Directorio `maps/`.

**`iploc --all`**  
Realiza las operaciones para poblar base de datos `--sync`, `-c` y `-g`. Y genera mapas `-M`.

![img](./maps/map_thumb.svg)

### Otras opciones

**`iploc <IP>`**
  - Muestra la información sobre \<IP\> disponible en ipinfo.io.  
  ```
  $ iploc 1.1.1.1

  ╭──────────┬──────────────────────────╮
  │ IP       │ 1.1.1.1                  │
  ├──────────┼──────────────────────────┤
  │ HOSTNAME │ one.one.one.one          │
  │ ANYCAST  │ Si                       │
  │ CUIDAD   │ Los Angeles              │
  │ REGION   │ California               │
  │ PAIS     │ US                       │
  │ GEOLOC   │ 34.0522,-118.2437        │
  │ ORGANIZ. │ AS13335 Cloudflare, Inc. │
  │ TimeZone │ America/Los_Angeles      │
  │ COD POST │ 90076                    │
  ╰──────────┴──────────────────────────╯
  ```

**`iploc -t <IP>`**
  - Muestra la información sobre \<IP\> disponible en ipinfo.io  
  usando el **token** especificado en `./config.cfg`.  

**`iploc -d <IP>`**
  - Muestra toda la información disponible en BD acerca de \<IP\>  
  ```
  $ iploc -d 37.139.6.60

  Consulta a base de datos:
  ╭───────────┬───────────────────────────╮
  │ IP        │ 37.139.6.60               │
  ├───────────┼───────────────────────────┤
  │ HOSTNAME  │ None                      │
  │ ANYCAST   │ Si                        │
  │ CUIDAD    │ Amsterdam                 │
  │ REGION    │ North Holland             │
  │ PAIS      │ NL                        │
  │ GEOLOC    │ 52.3740,4.8897            │
  │ ORGANIZ.  │ AS14061 DigitalOcean, LLC │
  │ FECHA REG │ Tue May 24 00:25:20 2022  │
  │ TimeZone  │ Europe/Amsterdam          │
  │ COD POST  │ 1012                      │
  ╰───────────┴───────────────────────────╯
  ╭──────────────────────────┬────────┬────────┬─────────────────────────╮
  │       Fecha visita       │ Codigo │ Metodo │ Request                 │
  ├──────────────────────────┼────────┼────────┼─────────────────────────┤
  │ Sun May 22 02:49:03 2022 │  301   │  HEAD  │ /                       │
  │ Sun May 22 02:49:04 2022 │  200   │  HEAD  │ /                       │
  │ Sun May 22 02:49:04 2022 │  301   │  GET   │ /wp-login.php           │
  │ Sun May 22 02:49:05 2022 │  404   │  GET   │ /wp-login.php           │
  │ Sun May 22 02:49:06 2022 │  301   │  GET   │ /wordpress/wp-login.php │
  │ Sun May 22 02:49:07 2022 │  404   │  GET   │ /wordpress/wp-login.php │
  │ Sun May 22 02:49:07 2022 │  301   │  GET   │ /blog/wp-login.php      │
  │ Sun May 22 02:49:08 2022 │  404   │  GET   │ /blog/wp-login.php      │
  │ Sun May 22 02:49:09 2022 │  301   │  GET   │ /wp/wp-login.php        │
  │ Sun May 22 02:49:10 2022 │  404   │  GET   │ /wp/wp-login.php        │
  ╰──────────────────────────┴────────┴────────┴─────────────────────────╯
  ```

**`iploc -f <archivo_IPs>`**
  - Muestra la información disponible en ipinfo.io para cada \<IP\>  
  en archivo pasado como argumento.  

**`iploc -D <archivo_IPs>`**
  - Muestra toda la información disponible en BD para cada \<IP\>  
  en archivo pasado como argumento.  

ej. formato `./archivo_IPs`.  
```
1.1.1.1
8.8.8.8
...
```  

### Sicronización manual

No es necesario el uso manual del script, ya que este es llamado por `iploc --sync`.  
Pero ya que existe, puede resultar conveniente tener la opción de llamar manualmente a las funciones.  

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
logdest=/home/server_user/nginx_log.old
```
Crear archivo de configuración **config.cfg**.   
ej. archivo de configuración `./config.cfg`
```cfg
[bash_script]
server_name=mi_server
ruta_base=mi_server://home/server_user/nginx_log.old/
server_script=//home/server_user/scripts/muevelogz.sh
destino_log=/home/local_user/.cache/nginx_old

[iplocate]
token = '?token=1234567890abc'
```
- ***mi_server***: parte de *ruta_base*, nombre del host según configuración en `~/.ssh/config`.  
- **ruta_base** : es la ruta en el servidor donde se mueven los logs archivados (.gz) desde  
`/var/log/nginx/` (termina en `/`).  
- **destino_log** : ruta donde se guardan local y temporalmente los archivos *log.?.gz*.  
- **server_name** : nombre del host según configuración en `~/.ssh/config`.  
- **server_script** : ruta en el servidor, del script que mueve los *log.?.gz*.



Correr `iploc -h` para crear base de datos.  

```
📂️ nginx_data/
├── 📁️ maps
├── 📄️ __init__.py
├── 📄️ config.cfg
├── 📄️ ipinfo.db
├── 📄️ iplocate.py
├── 📄️ mapsgen.py
├── 📄️ muevelog.sh
├── 📄️ muevelogz.sh
├── 📄️ README.md
└── 📄️ sql_alch.py
```

Seguir los pasos explicados en  [Uso](#uso).

### Dependencias
<br>

- Servidor:
  - Bash >= 5.0
  - rsync
  
<br>  
  
- Local:
  - Bash >= 5.1.16
  - SQLite3 3.38.5
  - Python >= 3.10
    - requests
    - SQLAlchemy 1.4.32
    - rich
    - py-staticmaps
  - sqlitebrowser 3.35.5 (opc.)
  
<br>  
  
- *[Token](https://ipinfo.io/)*


