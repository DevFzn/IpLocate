import sqlite3
import os
from rich.console import Console
from rich.table import Table
from rich import box

selfpath = os.path.abspath(os.path.dirname(__file__))
console = Console()
conn = sqlite3.connect(f'{selfpath}/../ipinfo.db')
c = conn.cursor()


# GeoLoc
def get_geoloc(codigo):
    if codigo == 200:
        consulta = """SELECT DISTINCT geoloc FROM registro WHERE ip in
                      (SELECT `ip` from visita WHERE cod_html=='200');"""
    else:
        consulta = """SELECT DISTINCT geoloc FROM registro WHERE ip in
                      (SELECT `ip` from visita WHERE cod_html!='200'
                      AND cod_html!='444' AND cod_html!='0'
                      AND cod_html!='404');"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


# Detalle Visitas por pais
def vistas_pais_detalle(pais, codigo=''):
    if codigo == '':
        consulta = f"""SELECT DATE(fecha, 'unixepoch') AS
                       fecha_local, ip, metodo, cod_html, consulta
                       FROM visita WHERE ip IN (SELECT `ip` FROM `registro`
                       WHERE `pais` = '{pais}');"""
    else:
        consulta = f"""SELECT DATE(fecha, 'unixepoch') AS
                       fecha_local, ip, metodo, cod_html, consulta
                       FROM visita WHERE ip IN (SELECT `ip` FROM `registro`
                       WHERE `pais` = '{pais}') and cod_html = '{codigo}';"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


def pt_visita_pais_detalle(pais, codigo=''):
    respuesta = vistas_pais_detalle(pais, codigo)
    if codigo != '':
        titulo = f"[bold][blue]Detalle visitas pais: [yellow]{pais}[blue] respuesta [/blue][yellow]{codigo}[/bold][yellow]"
    else:
        titulo = f"[bold][blue]Detalle visitas pais: [/blue][yellow]{pais}[/yellow][/bold]"
    tbl_v = Table(
            title=titulo,
            box=box.ROUNDED,
            show_lines=False,
            row_styles=["dim", ""],
            border_style="dark_magenta")
    tbl_v.add_column("Fecha", justify="center", style="bright_yellow")
    tbl_v.add_column("IP", justify="left", style="bright_cyan")
    tbl_v.add_column("Metodo", justify="left", style="bright_green")
    tbl_v.add_column("Respuesta", justify="left", style="bright_blue")
    tbl_v.add_column("Consulta", justify="left", style="yellow")
    for item in respuesta:
        tbl_v.add_row(str(item[0]), str(item[1]), str(item[2]),
                      str(item[3]), str(item[4]))
    console.print(tbl_v)


# Formato fecha -- Convertir fecha 'unixepoch' a 'localtime'
def unix_to_local_date():
    consulta = """
    SELECT DATE(fecha, 'unixepoch') AS fecha_local FROM visita;
    """
    c.execute(consulta)
    return c.fetchall()


# Select geoloc by cod html
# SELECT all from registro where ip=(SELECT ip from visita where cod_html=200);
def select_cod(codigo):
    consulta = f"""SELECT geoloc FROM registro WHERE ip IN
                   (SELECT ip FROM visita WHERE cod_html = {codigo});"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


# Select fecha mayor que (ej. 1661226920)
def sel_pais_desde(pais, unix_e):
    consulta = f"""SELECT DATE(fecha, 'unixepoch') AS
                   fecha_local, ip, metodo, cod_html, consulta
                   FROM visita WHERE ip IN (SELECT `ip` FROM
                   `registro` WHERE `pais` = '{pais}') and fecha > {unix_e};"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


def pt_sel_pais_fecha(pais, fecha_ux, fecha_loc):
    fecha = fecha_loc.split('/')
    fecha = fecha[2] + '/' + fecha[1] + '/' + fecha[0]
    respuesta = sel_pais_desde(pais, fecha_ux)
    tbl_v = Table(
            title=f"[bold][blue]Visitas {pais}, desde {fecha}[/blue][/bold]",
            box=box.ROUNDED,
            show_lines=False,
            row_styles=["dim", ""],
            border_style="dark_magenta")
    tbl_v.add_column("Fecha", justify="center", style="bright_yellow")
    tbl_v.add_column("IP", justify="left", style="bright_cyan")
    tbl_v.add_column("Metodo", justify="left", style="bright_green")
    tbl_v.add_column("Respuesta", justify="left", style="bright_blue")
    tbl_v.add_column("Consulta", justify="left", style="yellow")
    for item in respuesta:
        tbl_v.add_row(str(item[0]), str(item[1]),
                      str(item[2]), str(item[3]), str(item[4]))
    console.print(tbl_v)


# Top 50 paises
def top_paises(top):
    consulta = f"""SELECT registro.pais, count(registro.pais) as Visitas
                   FROM visita, registro WHERE visita.ip=registro.ip
                   GROUP BY pais ORDER BY count(*) DESC LIMIT {top};"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


def pt_top_paises(top):
    respuesta = top_paises(top)
    tbl_v = Table(title=f"[bold][blue]Vistas Top {top}[/blue][/bold]",
                  box=box.ROUNDED,
                  show_lines=False,
                  row_styles=["dim", ""],
                  border_style="dark_magenta")
    tbl_v.add_column("País", justify="center", style="bright_yellow")
    tbl_v.add_column("Visitas", justify="left", style="bright_cyan")
    for item in respuesta:
        tbl_v.add_row(str(item[0]), str(item[1]))

    console.print(tbl_v)


# respuesta HTML para pais=?
def cod_html_pais(pais):
    consulta = f"""SELECT cod_html, count(cod_html) AS Ocurrencias
                   FROM visita WHERE ip IN (SELECT `ip` FROM `registro`
                   WHERE `pais` = '{pais}') GROUP BY cod_html
                   ORDER BY count(*) DESC;"""
    c.execute(consulta)
    resp = c.fetchall()
    return resp


def pt_html_cod_pais(pais):
    respuesta = cod_html_pais(pais)
    tbl_v = Table(
        title=f"[bold][blue]Códigos html: [/blue][green]{pais}[/bold][/green]",
        box=box.ROUNDED,
        show_lines=False,
        row_styles=["dim", ""],
        border_style="dark_magenta")
    tbl_v.add_column("Código", justify="center", style="bright_yellow")
    tbl_v.add_column("Conteo", justify="left", style="bright_cyan")
    for item in respuesta:
        tbl_v.add_row(str(item[0]), str(item[1]))

    console.print(tbl_v)
