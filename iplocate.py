#!/usr/bin/env python

import os
import sys
import subprocess
import requests
import re
import configparser as cfg
from os.path import isfile
import sql_alch
from rich import box
from rich.console import Console
from rich.table import Table
import consultas.querys_sqlite as querys
import logging

selfpath = os.path.abspath(os.path.dirname(__file__))
ownip = requests.get('https://ifconfig.me/').text
parser = cfg.ConfigParser()
parser.read(f'{selfpath}/config.cfg')
token = parser.get('iplocate','token') 
token = token.strip("'")
muevelog = f'{selfpath}/muevelog.sh '
log_file = f'{selfpath}/log/iplocate.log'
console = Console()
#tkn=True
# IP validate https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
ip_regx = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
ip_local_regx = "^192\.168\.0\.([0-9]|[0-9][0-9]|[0-9][0-9][0-9])$"


def log_usage(proceso, info):
    usage_log = f"Proceso:[{proceso}] - Info: [{info}]"
    logging.info(usage_log)


def filtro_ip_propia(ip):
    return True if ip != ownip and not re.search(ip_local_regx, ip) else False 


def print_ipinfo(ip, tkn=True):
    if (re.search(ip_regx, ip)):
        try:
            ip_info = sql_alch.consulta_ip(ip, tkn)
        except Exception as ex:
            print(f'Exception sql_alch.consulta_ip({ip})\n',ex)
            ip_info = None
        if isinstance(ip_info, dict):
            print_tabla_ip(ip_info)
        elif isinstance(ip_info, list):
            lista_visitas=[]
            contad=0
            for tupla in ip_info:
                visita = []
                if contad < 1: 
                    for ind, val in enumerate(tupla):
                        if ind == 0:
                            ip_dict = dict()
                            for dato in str(val).split(';'):
                                ip_dict[dato.split("=")[0]] = dato.split("=")[1]
                            print_tabla_ip(ip_dict)
                        else:
                            visita.append(str(val).split(',')[3].split('=')[1]) #.ljust(24))
                            visita.append(str(val).split(',')[2].split('=')[1]) #.center(11))
                            metodo = (str(val).split(',')[4].split('=')[1])
                            metodo = '---' if metodo == 'None' else metodo #.center(10)
                            visita.append(metodo)
                            request = ''.join(str(val).split(',')[5].split('=')[1:])
                            # configurar wrap en tabla
                            #request = request[:86]+'...' if len(request) > 90 else request
                            request = '---' if request == 'None' else request
                            visita.append(request)
                else:
                    for ind, val in enumerate(tupla):
                        if ind > 0:
                            # aqui modificar para representar las nuevas columnas de tabla visita
                            visita.append(str(val).split(',')[3].split('=')[1]) #.ljust(24)
                            visita.append(str(val).split(',')[2].split('=')[1]) #.center(11)
                            metodo = (str(val).split(',')[4].split('=')[1])
                            metodo = '---' if metodo == 'None' else metodo #.center(10)
                            visita.append(metodo)
                            request = ''.join(str(val).split(',')[5].split('=')[1:])
                            # configurar wrap en tabla
                            #request = request[:86]+'...' if len(request) > 90 else request
                            request = '---' if request == 'None' else request
                            visita.append(request)
                lista_visitas.append(visita)
                contad+=1 
            print_tabla_visita(lista_visitas)
        else:
            console.print(f'[red]Error type(ip_info) = [/red][magenta]{type(ip_info)}[/magenta][red]][/red]')
    else:
        ipr = ip.split('\n')[0]
        console.print(f'[red][[/red][magenta]{ipr}[/magenta][red]] no es una IP válida![/red]')


def print_tabla_ip(ip_info):
    tbl_ip = Table(box = box.ROUNDED, highlight=True, border_style="dim plum1")
    tbl_ip.add_column("IP", justify="left", style="bold #005fff", no_wrap=True)
    tbl_ip.add_column(f"{ip_info['ip']}", justify="left", style="#00ff5f")
    try:
        if 'host' in ip_info:
            tbl_ip.add_row("HOSTNAME", ip_info['host'])
        elif 'hostname' in ip_info:
            tbl_ip.add_row("HOSTNAME", ip_info['hostname']) 
        if 'anycast' in ip_info:
            anycast = 'Si' if ip_info['anycast'] else 'No'
            tbl_ip.add_row("ANYCAST", anycast)
        if 'cuidad' in ip_info:
            tbl_ip.add_row("CUIDAD", ip_info['cuidad'])
        elif 'city' in ip_info:
            tbl_ip.add_row("CUIDAD", ip_info['city'])
        if 'region' in ip_info:
            tbl_ip.add_row("REGION", ip_info['region'])
        if 'pais' in ip_info:
            tbl_ip.add_row("PAIS", ip_info['pais'])
        elif 'country' in ip_info:
            tbl_ip.add_row("PAIS", ip_info['country'])
        if 'geoloc' in ip_info:
            tbl_ip.add_row("GEOLOC", ip_info['geoloc'])
        elif 'loc' in ip_info:
            tbl_ip.add_row("GEOLOC", ip_info['loc'])
        if 'organizacion' in ip_info:
            tbl_ip.add_row("ORGANIZ.", ip_info['organizacion'])
        elif 'org' in ip_info:
            tbl_ip.add_row("ORGANIZ.", ip_info['org'])
        if 'fecha_reg' in ip_info:
            tbl_ip.add_row("FECHA REG", ip_info['fecha_reg'])
        if 'tzone' in ip_info:
            tbl_ip.add_row("TimeZone", ip_info['tzone'])
        elif 'timezone' in ip_info:
            tbl_ip.add_row("TimeZone", ip_info['timezone'])
        if 'cod_post' in ip_info:
            tbl_ip.add_row("COD POST", ip_info['cod_post'])
        elif 'postal' in ip_info:
            tbl_ip.add_row("COD POST", ip_info['postal'])
    except Exception as ex:
        print('Exception ipl.print_tabla_ip(): ', ex)
    try:
        console.print(tbl_ip)
    except Exception as ex:
        print('Exception print(tabla_ip): ', ex)

def print_tabla_visita(lista_visitas):
    tbl_v = Table(box = box.ROUNDED, show_lines = False,row_styles=["dim", ""], border_style="dark_orange3")
    tbl_v.add_column("Fecha visita", justify="center", style="bright_yellow", no_wrap=True)
    tbl_v.add_column("Codigo", justify="center", style="bold dodger_blue2")
    tbl_v.add_column("Metodo", justify="center", style="bright_magenta")
    tbl_v.add_column("Request", justify="left", style="#00ff5f", overflow='fold', no_wrap=False)
    for item in lista_visitas:
        tbl_v.add_row(item[0], item[1], item[2], item[3])

    console.print(tbl_v)


def archivo_ips(ips, tkn=True):
    with open(ips, 'r') as lista:
            for linea in lista:
                if '\n' in linea:
                    linea = linea.split('\n')[0]
                print_ipinfo(linea, tkn)
    sys.exit(0)

def _sync():
    console.print('[bold yellow]Sincronizando logs del servidor(bash script)[/bold yellow]')
    subprocess.check_call(muevelog+"%s" % "--start", shell=True)



def main():
    if len(sys.argv) > 1:
        try: 
            match sys.argv[1]:
                case '--all':
                    _sync()
                    console.print('[bold yellow]Cargando logs en base de datos[/bold yellow]\n')
                    sql_alch.carga_logs()
                    console.print('[bold yellow]Registro de datos de ipinfo[/bold yellow]')
                    sql_alch.registro_ips()
                    console.print('[bold yellow]Generando mapa de visitas[/bold yellow]')
                    sql_alch.mapsgen()
                case '--sync':
                    _sync()
                case '-c':
                    console.print('[bold yellow]Cargando logs en base de datos[/bold yellow]\n')
                    sql_alch.carga_logs()
                case '-g':
                    console.print('[bold yellow]Registro de datos de ipinfo[/bold yellow]')
                    sql_alch.registro_ips()
                case '-d':
                    console.print('[bold yellow]Consulta a base de datos:[/bold yellow]')
                    ip = sys.argv[2]
                    print_ipinfo(ip, None)
                case '-D':
                    console.print('[bold yellow]Consulta por archivo a base de datos:[/bold yellow]')
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2], None)
                    else:
                        console.print(f'[red]Archivo [[/red][magenta]{sys.argv[2]}[/magenta]'
                                       '[red]] no es válido![/red]')
                        sys.exit(0)
                case '-f':
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2], False)
                    else:
                        console.print(f'[red]Archivo [[/red][magenta]{sys.argv[2]}[/magenta]'
                               '[red]] no es válido[/red]')
                        sys.exit(0)
                case '-F':
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2])
                    else:
                        console.print(f'[red]Archivo [[/red][magenta]{sys.argv[2]}[/magenta]'
                               '[red]] no es válido[/red]')
                        sys.exit(0)
                case '-h':
                    uso()
                    exit(0)
                case '-hq':
                    uso_consultas()
                    exit(0)
                case '-t':
                    ip = sys.argv[2]
                    print_ipinfo(ip)
                case '-M':
                    console.print('[bold yellow]Generando mapa de visitas[/bold yellow]')
                    sql_alch.mapsgen()
                case '-q':
                    match sys.argv[2]:
                        case '-p':
                            pais = sys.argv[3]
                            querys.pt_html_cod_pais(pais.upper())
                        case '--top':
                            top = sys.argv[3]
                            querys.pt_top_paises(top)
                        case '--pais-desde':
                            pais = sys.argv[3]
                            fecha_local = sys.argv[4]
                            fecha_unix = sql_alch.fecha_error_to_epoch(sys.argv[4]+' 00:00:00')
                            querys.pt_sel_pais_fecha(pais.upper(), fecha_unix, fecha_local)
                        case '--detalle-pais':
                            pais = sys.argv[3]
                            if len(sys.argv) > 4:
                                if sys.argv[4].isnumeric():
                                    codigo = sys.argv[4]
                                    querys.pt_visita_pais_detalle(pais.upper(), codigo)
                                else:
                                    console.print(f'[magenta]-q --detalle-pais <pais> [/magenta][red][bold]<CODIGO> inválido ({sys.argv[4]})[/bold][/red]')
                            else:
                                querys.pt_visita_pais_detalle(pais.upper())
                        case _:
                                console.print(f'[red] query desconocida [bold]{sys.argv[2]}[/bold][/red]')
                case _:
                    ip = sys.argv[1]
                    print_ipinfo(ip, False)
        except IndexError as ex:
            console.print('[red] error sys.args! [/red]', ex)
        finally:
            sys.exit(0)

    console.print("[green]Ingresa una[/green] [bold blue]IP [/bold blue]"
                  "[green]o [/green][bold blue]s [/bold blue]"
                  "[green]para salir:[/green]")
    while True:
        console.print("[bold blue] -> [/bold blue]", end='')
        ip = input()
        if ip in 'sq0SQnN':
            exit(0)
        print_ipinfo(ip)


def uso_consultas():
    ayuda = f"""
    [bold blue]ipLocate[/bold blue]

        [deep_sky_blue1]Reportes según consultas a base de datos.

        Uso: [deep_sky_blue1][bold][yellow]iploc -q[/yellow][blue] <consulta>[/bold][/blue]

    [deep_sky_blue1]Consultas a base de datos:[deep_sky_blue1]
    [bold yellow]-p[/bold yellow] [blue]<pais>[/blue]                           [green]- Conteo de respuestas html para <pais> (ejs. CL AR)[/green]
    [bold yellow]--top [/bold yellow][blue]<n>[/blue]                           [green]- Visitas top <n> paises[/green]
    [bold yellow]--pais-desde[/bold yellow][blue] <pais> <fecha>[/blue]         [green]- Detalle visitas <pais> desde <fecha> (ej. 2022/9/19)[/green]
    [bold yellow]--detalle-pais[/bold yellow][blue] <pais> opc(<cod>)[/blue]   [green] - Muestra al detalle las visitas desde <pais>,
                                          filtro por codigo opcional.[/green]
    """
    console.print(ayuda)

def uso():
    ayuda = f"""
    [bold blue]ipLocate[/bold blue]

        [deep_sky_blue1]Consulta en ipinfo.io (con o sin token) información sobre IP(s).
        Carga logs de nginx en base de datos.
        Consulta en ipinfo.io y registra en base de datos.
        Consultas y reportes según información en la base de datos.[/deep_sky_blue1]

        [bold yellow]iploc -h[/bold yellow]              [green]- Muestra esta ayuda.[/green]
        [bold yellow]iploc -hq[/bold yellow]             [green]- Ayuda sobre querys.[/green]
        
    [bold blue]Consultas ipinfo.io:[/bold blue]
        [bold yellow]iploc[/bold yellow] [blue]<IP>[/blue]            [green]- Consulta la información de <IP> disponible en ipinfo.io.[/green]
        [bold yellow]iploc -f [/bold yellow][blue]<archivo> [/blue]   [green]- Consulta info. de las IPs en <archivo> (ipinfo.io).[/green]
        [bold yellow]iploc -t [/bold yellow][blue]<IP>[/blue]         [green]- Consulta la info. de <IP> usando 'token' de ipinfo.io,
                                especificado en config.cfg.[/green]
        [bold yellow]iploc -F [/bold yellow][blue]<archivo> [/blue]   [green]- Consulta info. de las IPs en <archivo> (token ipinfo.io).[/green]

    [bold blue]Consultas base de datos:[/bold blue]
        [bold yellow]iploc -d [/bold yellow][blue]<IP>      [/blue]   [green]- Consulta la información de <IP> disponible en base de datos.[/green]
        [bold yellow]iploc -D [/bold yellow][blue]<archivo> [/blue]   [green]- Consulta info. de las IPs en <archivo> (base de datos).[/green]
        [bold yellow]iploc -M              [/bold yellow][green]- Genera mapa según registro en BD (cod. 200 y otros).[/green]

    [bold blue]Operaciones base de datos:[/bold blue]
        [bold yellow]iploc --sync          [/bold yellow][green]- Sincroniza logs del servidor (bash script).[/green]
        [bold yellow]iploc -c              [/bold yellow][green]- Carga logs en base de datos.[/green]
        [bold yellow]iploc -g              [/bold yellow][green]- Guarda ipinfo de IPs sin registro en la BD.[/green]
        [bold yellow]iploc --all           [/bold yellow][green]- Realiza las 3 operaciones para poblar BD (--sync, -c y -g) y -M.[/green]
    """
    console.print(ayuda)

if __name__ == "__main__":
    logging.basicConfig(
        filename = log_file,
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level = logging.INFO
        )
    logging.info("iplocate inicio")
    main()
