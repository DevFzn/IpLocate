import os
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, update
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select
import iplocate as ipl

logs_dir = ipl.parser.get('bash_script', 'destino_log')
logs_dir = logs_dir.strip("'")
base_de_datos = f'sqlite:////{ipl.selfpath}/ipinfo.db'

Base = declarative_base()

class Visita(Base):
    __tablename__ = 'visita'
    id       = Column(Integer, Sequence('visita_id_seq'), primary_key=True)
    ip       = Column(String)
    html     = Column(Integer)
    fecha    = Column(Integer)
    registro = Column(Integer, default=0) 

    def get_fecha(self):
        return time.asctime(time.localtime(int(self.fecha.__repr__())))

    def fecha_local(self):
        fecha_l = self.get_fecha()
        #fecha_l = time.asctime(self.fecha)
        return fecha_l
        #fecha_l = time.strftime(fecha_l)

    def consulta_registro(self):
        return True if self.registro == 1 else False

    def __repr__(self) -> str:
        return "ID: {}\nIP: {}\nHtmlCode: {}\n" \
               "Fecha: {}\nRegistrado: {}\n".format(
                        self.id, 
                        self.ip, 
                        self.html,
                        self.get_fecha(),
                        self.consulta_registro())


# Tabla registro ip info
class Registro(Base):
    __tablename__ = 'registro'
    id           = Column(Integer, Sequence('registro_id_seq'), primary_key=True)
    ip           = Column(String)
    hostname     = Column(String, nullable=True)
    anycast      = Column(String, nullable=True)
    cuidad       = Column(String, nullable=True)
    region       = Column(String, nullable=True)
    pais         = Column(String, nullable=True)
    geoloc       = Column(String, nullable=True)
    organizacion = Column(String, nullable=True)
    fecha_reg    = Column(Integer, default=int(time.mktime(time.localtime())))
    tzone        = Column(String, nullable=True)
    cod_post     = Column(String, nullable=True)
    link         = Column(String, nullable=True)


engine = create_engine(base_de_datos)
Base.metadata.create_all(engine)
#Base.metadata.create_all(engine.execution_options(synchronize_session="fetch"))
Session = sessionmaker(bind=engine)
session = Session()


# Formatos fechas logs:
"""
# access.log == reverse_access.log
#  error.log == reverse_error.log
fecha_error   = "2022/05/10 07:11:46"
fecha_access  = "10/May/2022:11:42:14 -0400".split(' ')[0]
"""

def fecha_access_to_epoch(fecha):
    """Convierte al fecha del formato entregado por access.log 
    y reverse_access.log(nginx) al formato unix epoch.
    
    :fecha: str Fecha
    :returns: int unix epoch fecha (secs)
    """
    fecha = datetime.strptime(fecha, '%d/%b/%Y:%H:%M:%S')
    fecha_unix = int(time.mktime(fecha.timetuple()))
    return fecha_unix

def fecha_error_to_epoch(fecha):
    """Convierte al fecha del formato entregado por error.log 
    y reverse_error.log (nginx) al formato unix epoch.
    
    :fecha_local: str Fecha
    :returns: int unix epoch fecha (secs)
    """
    fecha = datetime.strptime(fecha, '%Y/%m/%d %H:%M:%S')
    fecha_unix = int(time.mktime(fecha.timetuple()))
    return fecha_unix

def epoch_to_local(fecha):
    """Convierte fecha unix epoch a localtime

    :fecha: int Fecha (secs)
    :returns: str Fecha
    """
    return time.asctime(time.localtime(int(fecha)))


def ip_registrada(ip):
    ip_reg = session.query(Visita).filter(Visita.ip==ip).filter(Visita.registro==1).first()
    return 0 if ip_reg is None else ip_reg.registro


def carga_access_log(log):
    if os.path.exists(log):
        print(f'{ipl.co_Yel}Registrando [{log}]{ipl.co_rst}')
        try:
            with open(log, 'r') as lista:
                for linea in lista:
                    ip = linea.split(' ')[0]
                    if ipl.filtro_ip_propia(ip):
                        fecha = fecha_access_to_epoch(linea.split(' ')[3][1:])
                        codigo= int(linea.split('"')[2].split(' ')[1])
                        if ip_registrada(ip):
                            session.add(Visita(ip=ip, html=codigo, fecha=fecha, registro=1))
                        else:
                            session.add(Visita(ip=ip, html=codigo, fecha=fecha))
            session.commit()
            print(f'{ipl.co_Grn}Carga completa.. borrando log{ipl.co_rst}\n')
            os.remove(log)
            return True
        except:
            print(f'{ipl.co_Red}Ocurrio un error al intentar abrir/cargar: [{log}]{ipl.co_rst}\n')
            return False
    else:
        print(f'{ipl.co_Red}log: [{log}] inexistente.{ipl.co_rst}\n')
    return False


def carga_error_logs(log):
    if os.path.exists(log):
        print(f'{ipl.co_Yel}Registrando [{log}]{ipl.co_rst}')
        try:
            with open(log, 'r') as lista:
                for linea in lista:
                    ip = linea.split('client: ')[1].split(',')[0]
                    if ipl.filtro_ip_propia(ip):
                        fecha  = fecha_error_to_epoch(' '.join(linea.split()[0:2]))
                        codigo = 300
                        if ip_registrada(ip):
                            session.add(Visita(ip=ip, html=codigo, fecha=fecha, registro=1))
                        else:
                            session.add(Visita(ip=ip, html=codigo, fecha=fecha))
            session.commit()
            print(f'{ipl.co_Grn}Carga completa.. borrando log{ipl.co_rst}\n')
            os.remove(log)
            return True
        except:
            print(f'{ipl.co_Red}Ocurrio un error'+
                  f'al intentar abrir/cargar: [{log}]{ipl.co_rst}\n')
            return False
    else:
        print(f'{ipl.co_Red}log: [{log}] inexistente.{ipl.co_rst}\n')
        return False


def carga_logs():
    print(f'{ipl.co_Grn}Carga de logs en base de datos:{ipl.co_rst}\n')
    carga_access_log(logs_dir+'/access.log')
    carga_access_log(logs_dir+'/reverse-access.log')
    carga_error_logs(logs_dir+'/error.log')
    carga_error_logs(logs_dir+'/reverse-error.log')


def carga_registro_ip(ip_info):
    if not ip_registrada(ip_info['ip']):
        info_dic = {}
        info_dic['ip'] = ip_info['ip']
        info_dic['hostname'] = ip_info['hostname']  if 'hostname' in ip_info else None
        info_dic['anycast'] = ip_info['anycast'] if 'anycast' in ip_info else None
        info_dic['ciudad'] = ip_info['city'] if 'city' in ip_info else None
        info_dic['region'] = ip_info['region'] if 'region' in ip_info else None
        info_dic['pais'] = ip_info['country'] if 'country' in ip_info else None
        info_dic['geoloc'] = ip_info['loc'] if 'loc' in ip_info else None
        info_dic['organizacion'] = ip_info['org'] if 'org' in ip_info else None
        info_dic['tzone'] = ip_info['timezone'] if 'timezone' in ip_info else None
        info_dic['cod_post'] = ip_info['postal'] if 'postal' in ip_info else None
        info_dic['link'] = ip_info['readme'] if 'readme' in ip_info else None
        session.add(Registro( ip = info_dic['ip'],
                              hostname = info_dic['hostname'],
                              anycast = info_dic['anycast'],
                              cuidad = info_dic['ciudad'],
                              region = info_dic['region'],
                              pais = info_dic['pais'],
                              geoloc = info_dic['geoloc'],
                              organizacion = info_dic['organizacion'],
                              fecha_reg = int(time.mktime(time.localtime())),
                              tzone = info_dic['tzone'],
                              cod_post = info_dic['cod_post'],
                              link = info_dic['link'],
                              ))
        session.commit()
    stmt = update(Visita).where(Visita.ip == ip_info['ip']).values(registro=1).\
    execution_options(synchronize_session="fetch")
    #result = session.execute(stmt)
    session.execute(stmt)
    session.commit()


def registro_ips():
    registrar = True
    while registrar:
        statement = select(Visita).filter_by(registro=0)
        res = session.execute(statement).scalars().first()
        if res is None:
            print(f'{ipl.co_Grn}Registro ipinfo en DB finzalizado.{ipl.co_rst}')
            registrar = False
        #ip_actual= res.ip.split('\n')[0]
        ip_actual= res.ip
        ip_info = ipl.consulta_db(ip_actual)
        carga_registro_ip(ip_info)
