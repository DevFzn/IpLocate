#!/usr/bin/env python

import os
import sys
import subprocess
import requests
import re
import configparser as cfg
from os.path import isfile
from json import loads
from colorama import Fore, Back, Style
import sql_alch

selfpath = os.path.abspath(os.path.dirname(__file__))
ownip = requests.get('https://ifconfig.me/').text
parser = cfg.ConfigParser()
parser.read(f'{selfpath}/config.cfg')
token = parser.get('iplocate','token') 
token = token.strip("'")
muevelog = f'{selfpath}/muevelog.sh '
#tkn=True

# Colores
co_rst      = Style.RESET_ALL
co_Blu      = Fore.BLUE+Style.NORMAL
co_BluD     = Fore.BLUE+Style.DIM
co_BluB     = Fore.BLUE+Style.BRIGHT
co_Red      = Fore.RED+Style.NORMAL
co_RedD     = Fore.RED+Style.DIM
co_RedB     = Fore.RED+Style.BRIGHT
co_Grn      = Fore.GREEN+Style.NORMAL
co_GrnD     = Fore.GREEN+Style.DIM
co_GrnB     = Fore.GREEN+Style.BRIGHT
co_Yel      = Fore.YELLOW+Style.NORMAL
co_YelD     = Fore.YELLOW+Style.DIM
co_YelB     = Fore.YELLOW+Style.BRIGHT
co_BluLWh   = Fore.BLUE+Back.LIGHTWHITE_EX+Style.NORMAL
co_BluLWhB  = Fore.BLUE+Back.LIGHTWHITE_EX+Style.BRIGHT
co_GrnMgnB  = Fore.GREEN+Back.MAGENTA+Style.BRIGHT
co_RedBluD  = Fore.RED+Back.BLUE+Style.DIM
co_LRedBleD = Fore.LIGHTRED_EX+Back.BLUE+Style.DIM
co_BlkMgnB  = Fore.BLACK+Back.MAGENTA+Style.BRIGHT
co_BlkMgn   = Fore.BLACK+Back.MAGENTA+Style.NORMAL
co_LGrLBlk  = Fore.LIGHTGREEN_EX+Back.LIGHTBLACK_EX
co_RdYl     = Fore.RED+Back.YELLOW+Style.NORMAL
co_RdYlB    = Fore.RED+Back.YELLOW+Style.BRIGHT
co_BlkLBlkD = Fore.BLACK+Back.LIGHTBLACK_EX+Style.DIM
co_BluLBlkD = Fore.BLUE+Back.LIGHTBLACK_EX+Style.DIM
co_cuBlu    = '\33[38;5;122m'
# IP validate https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
ip_regx = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

def filtro_ip_propia(ip):
    return True if ip != ownip else False 


def consulta_ip(ip_consulta, tkn=True):
    if (re.search(ip_regx, ip_consulta)):
        match tkn:
            case True:
                consulta = f'https://ipinfo.io/{ip_consulta}{token}'
                info_ip = requests.get(consulta).text
                return loads(info_ip)
            case False:    
                consulta = f'https://ipinfo.io/{ip_consulta}'
                info_ip = requests.get(consulta).text
                return loads(info_ip)
            case None:
                resp = sql_alch.consulta_db(ip_consulta)
                #print('consulta_ip :', resp)
                return  resp
                # aqui va la consulta a base de datos


def print_ipinfo(ip, tkn=True):
    if (re.search(ip_regx, ip)):
        ip_info = consulta_ip(ip, tkn)
        if isinstance(ip_info, dict):
            for llave, valor in ip_info.items():
                print(f'{co_YelB}{llave}\b\t{co_Blu}->{co_rst} {co_Grn}{valor}{co_rst}')
            print(f'{co_RedB}------------------------------', end='')
            print(f'--------------------------------{co_rst}')
        elif isinstance(ip_info, list):
            contad=0
            for tupla in ip_info:
                if contad < 1: 
                    for ind, val in enumerate(tupla):
                        if ind == 0:
                            print(f'{co_BluD} _____________________________'
                                  f'________________________________{co_rst}')
                            for dato in str(val).split(';'):
                                print(f'{co_Blu}| {co_BluB}{dato.split("=")[0].ljust(12)}'
                                      f'{co_Blu}| {co_rst}{dato.split("=")[1]}{co_rst}')
                            print(f'{co_BluD} ________________________ __'
                                  f'_________ __________ _____________{co_rst}')
                            print(f'{co_Blu}|{co_YelB}      Fecha Visita      {co_rst}'
                                  f'{co_Blu}|{co_YelB}Codigo html{co_Blu}|'
                                  f'{co_YelB}  Metodo  {co_rst}'
                                  f'{co_Blu}|{co_YelB}   Request {co_rst}')
                            print(f'{co_Blu}|------------------------|--'
                                  f'---------|----------|-------------{co_rst}')
                        else:
                            # aqui modificar para representar las nuevas columnas de tabla visita
                            codig = str(val).split(',')[2].split('=')[1].center(11)
                            fecha = str(val).split(',')[3].split('=')[1].ljust(24)
                            metodo = (str(val).split(',')[4].split('=')[1])
                            metodo = '---'.center(10) if metodo == 'None' else metodo.center(10)
                            request = str(val).split(',')[5].split('=')[1]
                            request = request[:86]+'...' if len(request) > 90 else request
                            request = '---' if request == 'None' else request
                            #if len(request) > 90:
                            #    request = request[:86]+'...'
                            print(f'{co_Blu}|{co_Yel}{fecha}{co_rst}'
                                  f'{co_Blu}|{co_GrnB}{codig}'
                                  f'{co_Blu}|{co_Grn}{metodo}{co_rst}'
                                  f'{co_Blu}|{co_Grn}{request}{co_rst}')
                else:
                    for ind, val in enumerate(tupla):
                        if ind > 0:
                            # aqui modificar para representar las nuevas columnas de tabla visita
                            codig = str(val).split(',')[2].split('=')[1].center(11)
                            fecha = str(val).split(',')[3].split('=')[1].ljust(24)
                            metodo = (str(val).split(',')[4].split('=')[1])
                            metodo = '---'.center(10) if metodo == 'None' else metodo.center(10)
                            request = str(val).split(',')[5].split('=')[1]
                            request = request[:86]+'...' if len(request) > 90 else request
                            request = '---' if request == 'None' else request
                            print(f'{co_Blu}|{co_Yel}{fecha}{co_rst}'
                                  f'{co_Blu}|{co_GrnB}{codig}'
                                  f'{co_Blu}|{co_Grn}{metodo}{co_rst}'
                                  f'{co_Blu}|{co_Grn}{request}{co_rst}')
                contad+=1
            print(f'{co_RedB}-------------------------------'
                  f'-------------------------------{co_rst}')
        else:
            print('otra wea: ', type(ip_info))
    else:
        ipr = ip.split('\n')[0]
        print(f'{co_Red}[{co_BlkMgn}{ipr}{co_rst}{co_Red}] no es una IP válida!{co_rst}')


def archivo_ips(ips, tkn=True):
    with open(ips, 'r') as lista:
        for linea in lista:
            if '\n' in linea:
                linea = linea.split('\n')[0]
            print_ipinfo(linea, tkn)
    sys.exit(0)


def main():
    if len(sys.argv) > 1:
        try: 
            match sys.argv[1]:
                case '--sync':
                    print(f'{co_YelB}Sincronizando logs del servidor(bash script){co_rst}')
                    subprocess.check_call(
                            muevelog+"%s" % "--start",
                            shell=True)
                case '-c':
                    print(f'{co_YelB}Cargando logs en base de datos{co_rst}')
                    sql_alch.carga_logs()
                case '-d':
                    print(f'{co_YelB}Consulta base de datos:{co_rst}')
                    ip = sys.argv[2]
                    print_ipinfo(ip, None)
                case '-D':
                    print(f'{co_YelB}Consulta por archivo en base de datos:{co_rst}')
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2], None)
                    else:
                        print(f'{co_Red}Archivo [{co_BlkMgn}{sys.argv[2]}'+
                              f'{co_rst}{co_Red}] no es válido''')
                        sys.exit(0)
                case '-g':
                    print(f'{co_YelB}Registrando datos de ipinfo{co_rst}')
                    sql_alch.registro_ips()
                case '-f':
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2], False)
                    else:
                        print(f'{co_Red}Archivo [{co_BlkMgn}{sys.argv[2]}'+
                              f'{co_rst}{co_Red}] no es válido''')
                        sys.exit(0)
                case '-F':
                    if isfile(sys.argv[2]):
                        archivo_ips(sys.argv[2])
                    else:
                        print(f'{co_Red}Archivo [{co_BlkMgn}{sys.argv[2]}'+
                              f'{co_rst}{co_Red}] no es válido''')
                        sys.exit(0)
                case '-h':
                    uso()
                    exit(0)
                case '-t':
                    ip = sys.argv[2]
                    print_ipinfo(ip)
                case _:
                    ip = sys.argv[1]
                    print_ipinfo(ip, False)
        except IndexError:
            print(f'{co_Red} error sys.args! {co_rst}')
        finally:
            sys.exit(0)

    print(f'{co_Grn}Ingresa una {co_BluB}IP {co_Grn}o {co_BluB}s '+
          f'{co_Grn}para salir:{co_rst}')
    while True:
        ip = input(f'{co_BluB} -> {co_rst}')
        if ip in 'sq0SQnN':
            exit(0)
        print_ipinfo(ip)


def uso():
    ayuda = f"""
    {co_BluB}ipLocate{co_rst}
        {co_cuBlu}Consulta información sobre IP(s) disponibles en ipinfo.io con o sin token.
        Carga logs de nginx en base de datos. Consulta con ipinfo.io y registra
        en base de datos.
        Consultas y reportes según información en la base de datos.{co_rst}

        {co_YelB}iploc -h               {co_Grn}- Muestra esta ayuda.{co_rst}

    {co_BluB}Uso para consultas:{co_rst}
        {co_YelB}iploc {co_Blu}<IP>             {co_Grn}- Consulta la información de <IP> disponible en ipinfo.io.{co_rst}
        {co_YelB}iploc -t {co_Blu}<IP>          {co_Grn}- Consulta la info. de <IP> usando 'token' de ipinfo.io,
                                 especificado en config.cfg.{co_rst}
        {co_YelB}iploc -d {co_Blu}<IP>          {co_Grn}- Consulta la información de <IP> disponible en base de datos.{co_rst}
        {co_YelB}iploc -f {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (ipinfo.io).{co_rst}
        {co_YelB}iploc -F {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (token, ipinfo.io).{co_rst}
        {co_YelB}iploc -D {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (base de datos).{co_rst}

    {co_BluB}Operaciones base de datos:{co_rst}
        {co_YelB}iploc --sync           {co_Grn}- Sincroniza logs del servidor (bash script).{co_rst}
        {co_YelB}iploc -c               {co_Grn}- Carga logs en base de datos.{co_rst}
        {co_YelB}iploc -g               {co_Grn}- Guarda ipinfo de IPs sin registro en la BD.{co_rst}

    """
    print(ayuda)

if __name__ == "__main__":
    main()
