import os
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, update
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ForeignKey
import iplocate as ipl

logs_dir = ipl.parser.get('bash_script', 'destino_log')
logs_dir = logs_dir.strip("'")
base_de_datos = f'sqlite:////{ipl.selfpath}/ipinfo.db'

Base = declarative_base()

# Tabla registro ip info
class Registro(Base):
    __tablename__ = 'registro'
    ip           = Column(String, primary_key=True)
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
    #link         = Column(String, nullable=True)
    visitas      = relationship("Visita",
                                order_by="Visita.id",
                                back_populates="visita_ip",
                                cascade="all, delete, delete-orphan")

    def get_fecha(self):
        return time.asctime(time.localtime(int(self.fecha_reg.__repr__())))


    def __repr__(self) -> str:
        #print('en repr')
        try:
            rep = f'ip={self.ip};host={self.hostname};anycast={self.anycast};'+\
                  f'cuidad={self.cuidad};region={self.region};pais={self.pais};'+\
                  f'geoloc={self.geoloc};organizacion={self.organizacion};'+\
                  f'fecha_reg={self.get_fecha()};tzone={self.tzone};cod_post={self.cod_post}'
            #print('Repr:', rep)
            return rep
        except Exception as ex:
            print('Exception :', ex)
            return "error repr"


class Visita(Base):
    __tablename__ = 'visita'
    id       = Column(Integer, Sequence('visita_id_seq'), primary_key=True)
    ip       = Column(String, ForeignKey('registro.ip'))
    html     = Column(Integer)
    fecha    = Column(Integer)
    registro = Column(Integer, default=0) 
    visita_ip  = relationship("Registro", back_populates="visitas")
    

    def get_fecha(self):
        return time.asctime(time.localtime(int(self.fecha.__repr__())))

    def consulta_registro(self):
        return True if self.registro == 1 else False

    def __repr__(self) -> str:
        try:
            rep = f'id={self.id},ip={self.ip},html={self.html},fecha={self.get_fecha()}'
            return rep
        except Exception as ex:
            print('Exception :', ex)
            return "Error repr Visita"


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
    try:
        ip_reg = session.query(Visita).filter(Visita.ip==ip).filter(Visita.registro==1).first()
    except Exception as ex:
        print('Exception', ex)
        ip_reg = None
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
            print(f'{ipl.co_Red}Error al intentar abrir/cargar: '+
                  f'[{ipl.co_rst}{log}{ipl.co_Red}]\n')
            return False
    else:
        print(f'{ipl.co_RedB}log: [{ipl.co_rst}{log}{ipl.co_RedB}]'+ 
              f' inexistente.{ipl.co_rst}\n')
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
            print(f'{ipl.co_Red}Error al intentar abrir/cargar: '+
                  f'[{ipl.co_rst}{log}{ipl.co_Red}]\n')
            return False
    else:
        print(f'{ipl.co_RedB}log: [{ipl.co_rst}{log}{ipl.co_RedB}]'+ 
              f' inexistente.{ipl.co_rst}\n')
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
        try:
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
                                  ))
            session.commit()
        except Exception as ex:
            print('Exception: ', ex)
    stmt = update(Visita).where(Visita.ip == ip_info['ip']).values(registro=1).\
    execution_options(synchronize_session="fetch")
    #result = session.execute(stmt)
    try:
        session.execute(stmt)
        session.commit()
    except Exception as ex:
        print('Exception: ', ex)

def consulta_db(ip):
    try:
        statement = session.query(Registro, Visita).join('visitas').filter_by(ip=ip)
        result = session.execute(statement).all()
        return result
    except Exception as ex:
        print('Exception consulta_db:\n', ex)


def test_db():
    try:
        session.add(Visita(ip='dummy_ip', html=000, fecha=int(time.mktime(time.localtime()))))
        session.commit()
        session.add(Registro(ip ='dummy_ip'))
        session.commit()
    except Exception as ex:
        print('Exception: ', ex)


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
        ip_info = ipl.consulta_ip(ip_actual, True)
        carga_registro_ip(ip_info)
