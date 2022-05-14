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


def consulta_db(ip_consulta):
    consulta = f'https://ipinfo.io/{ip_consulta}{token}'
    info_ip = requests.get(consulta).text
    return loads(info_ip)


def consulta(ip_consulta):
    consulta = f'https://ipinfo.io/{ip_consulta}'
    info_ip = requests.get(consulta).text
    info_ip = loads(info_ip)
    for llave, valor in info_ip.items():
        print(f'{co_YelB}{llave}\b\t{co_Blu}->{co_rst} {co_Grn}{valor}{co_rst}')


def ipLocate(ip):
    if (re.search(ip_regx, ip)):
        consulta(ip)
        print(f'{co_RedB}------------------------------', end='')
        print(f'--------------------------------{co_rst}')
    else:
        ipr = ip.split('\n')[0]
        print(f'{co_Red}[{co_BlkMgn}{ipr}{co_rst}{co_Red}] no es una IP válida!{co_rst}')


def archivo_ips(ips):
    with open(ips, 'r') as lista:
        for linea in lista:
            ipLocate(linea)
    sys.exit(0)


def main():
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
            case '-g':
                print(f'{co_YelB}Registrando datos de ipinfo{co_rst}')
                sql_alch.registro_ips()
            case '-f':
                if isfile(sys.argv[2]):
                    archivo_ips(sys.argv[2])
                else:
                    print(f'{co_Red}Archivo [{co_BlkMgn}{sys.argv[2]}'+
                          f'{co_rst}{co_Red}] no es válido''')
                    sys.exit(0)
            case '-h':
                uso()
                exit(0)
            case _:
                ip = sys.argv[1]
                ipLocate(ip)
    except IndexError:
        print(f'\n{co_Blu}Ingresa una {co_BluB}IP o \'s\' ',end='')
        print(f'{co_Blu}para salir:{co_rst}')
        while True:
            ip = input(f'{co_BluB} -> {co_rst}')
            if ip in 'sq0SQnN':
                exit(0)
            ipLocate(ip)
    finally:
        sys.exit(0)


def uso():
    ayuda = f"""
    {co_BluB}ipLocate{co_rst}
        {co_cuBlu}Muestra información disponible en ipinfo.io sobre IPs consultadas.{co_rst}

    {co_BluB}Uso:{co_rst}
        {co_YelB}iploc {co_Blu}<IP>             {co_Grn}- Muestra la información de <IP>.{co_rst}
        {co_YelB}iploc -f {co_Blu}<archivo>     {co_Grn}- Muestra info. de las IPs en <archivo>
        {co_YelB}iploc -c               {co_Grn}- Carga logs en base de datos.{co_rst}
        {co_YelB}iploc -g               {co_Grn}- Guarda ipinfo de IPs sin registro en la BD.{co_rst}
        {co_YelB}iploc -h               {co_Grn}- Muestra esta ayuda.{co_rst}
        {co_YelB}iploc --sync           {co_Grn}- Sincroniza logs del servidor (bash script).{co_rst}

    """
    print(ayuda)

if __name__ == "__main__":
    main()
