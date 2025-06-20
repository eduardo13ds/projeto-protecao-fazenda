# app/models/__init__.py
from .usuario import Usuario
from .nivel_acesso import NivelAcesso
from .documentos_verificacao import DocumentoVerificacao
from .fazenda import Fazenda
from .dispositivo import Dispositivo
from .sensor import Sensor
from .tipo_sensor import TipoSensor
from .registro_leitura import RegistroLeitura
from .atuador import Atuador
from .tipo_atuador import TipoAtuador
from .registro_comando_atuador import RegistroComandoAtuador
from .alerta import Alerta
from .tabelas_associacao import usuario_fazenda_acesso, area_sensor_association, area_atuador_association

__all__ = [
    'Usuario',
    'NivelAcesso',
    'DocumentoVerificacao',
    'Fazenda',
    'Dispositivo',
    'Sensor',
    'TipoSensor',
    'RegistroLeitura',
    'Atuador',
    'TipoAtuador',
    'RegistroComandoAtuador',
    'Alerta',
    'usuario_fazenda_acesso',
    'area_sensor_association',
    'area_atuador_association'
]
