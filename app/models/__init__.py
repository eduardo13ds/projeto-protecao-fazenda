# app/models/__init__.py

# Importa a tabela de associação primeiro, se aplicável
from .tabelas_associacao import usuario_fazenda_acesso

# Importa todas as suas classes de modelo
from .nivel_acesso import NivelAcesso
from .usuario import Usuario
from .fazenda import Fazenda
from .tipo_sensor import TipoSensor
from .tipo_atuador import TipoAtuador
from .sensor import Sensor
from .atuador import Atuador
from .registro_leitura import RegistroLeitura
from .alerta import Alerta
from .registro_comando_atuador import RegistroComandoAtuador

# Você pode definir uma lista __all__ para exportar, se desejar
__all__ = [
    'usuario_fazenda_acesso',
    'NivelAcesso', 'Usuario', 'Fazenda', 'TipoSensor',
    'TipoAtuador', 'Sensor', 'Atuador', 'RegistroLeitura',
    'Alerta', 'RegistroComandoAtuador'
]