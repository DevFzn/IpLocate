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
                return  {}
                # aqui va la consulta a base de datos


def print_ipinfo(ip, tkn=True):
    if (re.search(ip_regx, ip)):
        ip_info = consulta_ip(ip, tkn)
        for llave, valor in ip_info.items():
            print(f'{co_YelB}{llave}\b\t{co_Blu}->{co_rst} {co_Grn}{valor}{co_rst}')
        print(f'{co_RedB}------------------------------', end='')
        print(f'--------------------------------{co_rst}')
    else:
        ipr = ip.split('\n')[0]
        print(f'{co_Red}[{co_BlkMgn}{ipr}{co_rst}{co_Red}] no es una IP válida!{co_rst}')


def archivo_ips(ips, tkn=True):
    with open(ips, 'r') as lista:
        for linea in lista:
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
                    print(f'{co_YelB}test_db-d{co_rst}')
                    # PENDIENTE # PENDIENTE
                    #sql_alch.test_db()
                case '-D':
                    print(f'{co_YelB}test_db-D{co_rst}')
                    # PENDIENTE # PENDIENTE
                    #sql_alch.test_db()
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
        {co_cuBlu}Muestra información disponible en ipinfo.io sobre IPs consultadas.{co_rst}

    {co_BluB}Uso:{co_rst}
        {co_YelB}iploc {co_Blu}<IP>             {co_Grn}- Consulta la información de <IP> disponible en ipinfo.io.{co_rst}
        {co_YelB}iploc -t {co_Blu}<IP>          {co_Grn}- Consulta la info. de <IP> usando 'token' de ipinfo.io,
                                 especificado en config.cfg.{co_rst}
        {co_YelB}iploc -d {co_Blu}<IP>          {co_Grn}- Consulta la información de <IP> disponible en base de datos.{co_rst}
        {co_YelB}iploc -f {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (ipinfo.io).{co_rst}
        {co_YelB}iploc -F {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (token, ipinfo.io).{co_rst}
        {co_YelB}iploc -D {co_Blu}<archivo>     {co_Grn}- Consulta info. de las IPs en <archivo> (base de datos).{co_rst}
        {co_YelB}iploc -c               {co_Grn}- Carga logs en base de datos.{co_rst}
        {co_YelB}iploc -g               {co_Grn}- Guarda ipinfo de IPs sin registro en la BD.{co_rst}
        {co_YelB}iploc -h               {co_Grn}- Muestra esta ayuda.{co_rst}
        {co_YelB}iploc --sync           {co_Grn}- Sincroniza logs del servidor (bash script).{co_rst}

    """
    print(ayuda)

if __name__ == "__main__":
    main()
