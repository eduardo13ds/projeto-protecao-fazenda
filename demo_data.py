#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados de exemplo para demonstração
Execute este script para ter dados iniciais no sistema StormGuard
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.nivel_acesso import NivelAcesso
from app.models.fazenda import Fazenda
from app.models.tipo_sensor import TipoSensor
from app.models.tipo_atuador import TipoAtuador
from app.models.dispositivo import Dispositivo
from app.models.sensor import Sensor
from app.models.atuador import Atuador
from app.models.registro_leitura import RegistroLeitura
from app.models.alerta import Alerta
from app.models.registro_comando_atuador import RegistroComandoAtuador


def clear_database():
    """Limpa todos os dados do banco de dados."""
    print("🗑️  Limpando banco de dados...")

    # Ordem importante para evitar violações de chave estrangeira
    db.session.query(RegistroComandoAtuador).delete()
    db.session.query(RegistroLeitura).delete()
    db.session.query(Alerta).delete()
    db.session.query(Sensor).delete()
    db.session.query(Atuador).delete()
    db.session.query(Dispositivo).delete()
    db.session.query(Fazenda).delete()
    db.session.query(Usuario).delete()
    db.session.query(TipoSensor).delete()
    db.session.query(TipoAtuador).delete()
    db.session.query(NivelAcesso).delete()

    db.session.commit()
    print("✅ Banco de dados limpo!")


def create_access_levels():
    """Cria os níveis de acesso básicos."""
    print("👥 Criando níveis de acesso...")

    levels = [
        {
            'nome_nivel': 'Administrador',
            'descricao': 'Acesso total ao sistema, pode gerenciar usuários e configurações'
        },
        {
            'nome_nivel': 'Gerente',
            'descricao': 'Acesso à gestão da fazenda, relatórios e alertas'
        },
        {
            'nome_nivel': 'Operador',
            'descricao': 'Acesso básico aos dados e alertas da fazenda'
        },
        {
            'nome_nivel': 'Visualizador',
            'descricao': 'Apenas visualização de dados e relatórios'
        }
    ]

    for level_data in levels:
        level = NivelAcesso(**level_data)
        db.session.add(level)

    db.session.commit()
    print(f"✅ {len(levels)} níveis de acesso criados!")


def create_users():
    """Cria usuários de demonstração."""
    print("👤 Criando usuários...")

    users = [
        {
            'nome_usuario': 'admin',
            'nome_completo': 'Administrador do Sistema',
            'email': 'admin@stormguard.com',
            'password': 'admin123'
        },
        {
            'nome_usuario': 'joao.silva',
            'nome_completo': 'João Silva',
            'email': 'joao.silva@fazenda.com',
            'password': 'joao123'
        },
        {
            'nome_usuario': 'maria.santos',
            'nome_completo': 'Maria Santos',
            'email': 'maria.santos@fazenda.com',
            'password': 'maria123'
        },
        {
            'nome_usuario': 'carlos.oliveira',
            'nome_completo': 'Carlos Oliveira',
            'email': 'carlos.oliveira@fazenda.com',
            'password': 'carlos123'
        }
    ]

    for user_data in users:
        password = user_data.pop('password')
        user = Usuario(**user_data)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    print(f"✅ {len(users)} usuários criados!")


def create_farms():
    """Cria fazendas de demonstração."""
    print("🚜 Criando fazendas...")

    farms = [
        {
            'nome_fazenda': 'Fazenda São José',
            'localizacao_latitude': -15.7942,
            'localizacao_longitude': -47.8822,
            'area_total_hectares': 250.50,
            'descricao': 'Fazenda especializada em cultivo de soja e milho'
        },
        {
            'nome_fazenda': 'Fazenda Boa Vista',
            'localizacao_latitude': -22.9068,
            'localizacao_longitude': -43.1729,
            'area_total_hectares': 180.25,
            'descricao': 'Fazenda focada em pecuária e agricultura familiar'
        },
        {
            'nome_fazenda': 'Fazenda Santa Maria',
            'localizacao_latitude': -23.5505,
            'localizacao_longitude': -46.6333,
            'area_total_hectares': 320.75,
            'descricao': 'Grande fazenda com cultivo diversificado'
        }
    ]

    for farm_data in farms:
        farm = Fazenda(**farm_data)
        db.session.add(farm)

    db.session.commit()
    print(f"✅ {len(farms)} fazendas criadas!")


def create_sensor_types():
    """Cria tipos de sensores."""
    print("🌡️  Criando tipos de sensores...")

    sensor_types = [
        {'nome_tipo': 'Temperatura', 'unidade_medida': '°C'},
        {'nome_tipo': 'Umidade', 'unidade_medida': '%'},
        {'nome_tipo': 'Pressão Atmosférica', 'unidade_medida': 'hPa'},
        {'nome_tipo': 'Velocidade do Vento', 'unidade_medida': 'm/s'},
        {'nome_tipo': 'Direção do Vento', 'unidade_medida': '°'},
        {'nome_tipo': 'Precipitação', 'unidade_medida': 'mm'},
        {'nome_tipo': 'Radiação Solar', 'unidade_medida': 'W/m²'},
        {'nome_tipo': 'pH do Solo', 'unidade_medida': 'pH'},
        {'nome_tipo': 'Condutividade Elétrica', 'unidade_medida': 'mS/cm'},
        {'nome_tipo': 'Luminosidade', 'unidade_medida': 'lux'}
    ]

    for sensor_type_data in sensor_types:
        sensor_type = TipoSensor(**sensor_type_data)
        db.session.add(sensor_type)

    db.session.commit()
    print(f"✅ {len(sensor_types)} tipos de sensores criados!")


def create_actuator_types():
    """Cria tipos de atuadores."""
    print("🤖 Criando tipos de atuadores...")

    actuator_types = [
        {'nome_tipo': 'Sistema de Irrigação'},
        {'nome_tipo': 'Ventilador'},
        {'nome_tipo': 'Aquecedor'},
        {'nome_tipo': 'Bomba d\'água'},
        {'nome_tipo': 'Válvula Solenoide'},
        {'nome_tipo': 'Motor de Portão'},
        {'nome_tipo': 'Sistema de Nebulização'},
        {'nome_tipo': 'Alarme Sonoro'}
    ]

    for actuator_type_data in actuator_types:
        actuator_type = TipoAtuador(**actuator_type_data)
        db.session.add(actuator_type)

    db.session.commit()
    print(f"✅ {len(actuator_types)} tipos de atuadores criados!")


def create_devices():
    """Cria dispositivos IoT."""
    print("📡 Criando dispositivos IoT...")

    devices = [
        {
            'identificador_unico': 'sensor_area_central_01',
            'nome_amigavel': 'Estação Central Principal',
            'area': 'Central',
            'id_fazenda': 1,
            'status': 'Ativo'
        },
        {
            'identificador_unico': 'sensor_area_norte_01',
            'nome_amigavel': 'Sensor Norte - Campo A',
            'area': 'Norte',
            'id_fazenda': 1,
            'status': 'Ativo'
        },
        {
            'identificador_unico': 'sensor_area_sul_01',
            'nome_amigavel': 'Sensor Sul - Estufa 1',
            'area': 'Sul',
            'id_fazenda': 1,
            'status': 'Ativo'
        },
        {
            'identificador_unico': 'sensor_area_leste_01',
            'nome_amigavel': 'Sensor Leste - Pastagem',
            'area': 'Leste',
            'id_fazenda': 2,
            'status': 'Ativo'
        },
        {
            'identificador_unico': 'sensor_area_oeste_01',
            'nome_amigavel': 'Sensor Oeste - Reservatório',
            'area': 'Oeste',
            'id_fazenda': 2,
            'status': 'Manutenção'
        },
        {
            'identificador_unico': 'sensor_central_fazenda3',
            'nome_amigavel': 'Central de Monitoramento',
            'area': 'Central',
            'id_fazenda': 3,
            'status': 'Ativo'
        }
    ]

    for device_data in devices:
        device = Dispositivo(**device_data)
        device.data_instalacao = datetime.utcnow() - timedelta(days=random.randint(30, 365))
        if device.status == 'Ativo':
            device.ultimo_ping = datetime.utcnow() - timedelta(minutes=random.randint(1, 5))
        db.session.add(device)

    db.session.commit()
    print(f"✅ {len(devices)} dispositivos criados!")


def create_sensors():
    """Cria sensores associados aos dispositivos."""
    print("🔬 Criando sensores...")

    devices = Dispositivo.query.all()
    sensor_types = TipoSensor.query.all()

    sensors_created = 0

    for device in devices:
        # Cada dispositivo terá alguns sensores aleatórios
        num_sensors = random.randint(3, 6)
        selected_types = random.sample(sensor_types, min(num_sensors, len(sensor_types)))

        for sensor_type in selected_types:
            sensor = Sensor(
                id_dispositivo=device.id_dispositivo,
                id_tipo_sensor=sensor_type.id_tipo_sensor,
                status='Ativo'
            )

            # Definir limites de alerta baseados no tipo de sensor
            if 'temperatura' in sensor_type.nome_tipo.lower():
                sensor.limite_minimo_alerta = 5.0
                sensor.limite_maximo_alerta = 40.0
            elif 'umidade' in sensor_type.nome_tipo.lower():
                sensor.limite_minimo_alerta = 20.0
                sensor.limite_maximo_alerta = 90.0
            elif 'pressao' in sensor_type.nome_tipo.lower():
                sensor.limite_minimo_alerta = 980.0
                sensor.limite_maximo_alerta = 1050.0

            sensor.ultima_leitura = datetime.utcnow() - timedelta(minutes=random.randint(1, 10))
            db.session.add(sensor)
            sensors_created += 1

    db.session.commit()
    print(f"✅ {sensors_created} sensores criados!")


def create_actuators():
    """Cria atuadores."""
    print("⚙️  Criando atuadores...")

    farms = Fazenda.query.all()
    actuator_types = TipoAtuador.query.all()

    actuators = []

    for farm in farms:
        # Cada fazenda terá alguns atuadores
        num_actuators = random.randint(2, 4)

        for i in range(num_actuators):
            actuator_type = random.choice(actuator_types)

            actuator = Atuador(
                nome_atuador=f"{actuator_type.nome_tipo} - {farm.nome_fazenda} #{i+1}",
                id_tipo_atuador=actuator_type.id_tipo_atuador,
                id_fazenda=farm.id_fazenda,
                status_atual='Desligado',
                endereco_logico=f"192.168.1.{100 + len(actuators)}",
                fabricante_modelo=random.choice(['Siemens S7-1200', 'Allen Bradley', 'Schneider Electric', 'ABB AC500'])
            )

            actuators.append(actuator)
            db.session.add(actuator)

    db.session.commit()
    print(f"✅ {len(actuators)} atuadores criados!")


def create_sensor_readings():
    """Cria leituras históricas dos sensores."""
    print("📊 Criando leituras históricas dos sensores...")

    sensors = Sensor.query.all()
    readings_created = 0

    # Criar leituras para os últimos 7 dias
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    for sensor in sensors:
        current_time = start_time

        while current_time <= end_time:
            # Gerar valor baseado no tipo de sensor
            if 'temperatura' in sensor.tipo_sensor.nome_tipo.lower():
                base_value = 25.0
                variation = random.uniform(-8, 10)
                # Variação diurna
                hour_factor = abs(12 - current_time.hour) / 12
                value = base_value + variation + (hour_factor * 5)

            elif 'umidade' in sensor.tipo_sensor.nome_tipo.lower():
                base_value = 65.0
                variation = random.uniform(-25, 25)
                # Umidade inversa à temperatura
                hour_factor = (12 - abs(12 - current_time.hour)) / 12
                value = base_value + variation + (hour_factor * 10)

            elif 'pressao' in sensor.tipo_sensor.nome_tipo.lower():
                value = random.uniform(990, 1025)

            elif 'vento' in sensor.tipo_sensor.nome_tipo.lower():
                value = random.uniform(0, 15)

            elif 'precipitacao' in sensor.tipo_sensor.nome_tipo.lower():
                # Precipitação é esporádica
                if random.random() < 0.15:  # 15% de chance de chuva
                    value = random.uniform(0.1, 25.0)
                else:
                    value = 0.0

            else:
                value = random.uniform(0, 100)

            # Determinar qualidade da leitura
            quality = 'Confiavel'
            if random.random() < 0.05:  # 5% de chance de ruído
                quality = 'Ruido'
                value = value * random.uniform(0.5, 1.5)
            elif random.random() < 0.02:  # 2% de chance de fora da faixa
                quality = 'Fora da Faixa'
                value = value * random.uniform(2, 5)

            reading = RegistroLeitura(
                id_sensor=sensor.id_sensor,
                valor_leitura=f"{value:.2f}",
                timestamp_leitura=current_time,
                qualidade=quality,
                valor_numerico=round(value, 2),
                unidade_medida=sensor.tipo_sensor.unidade_medida
            )

            db.session.add(reading)
            readings_created += 1

            # Próxima leitura (intervalo aleatório entre 30 min e 2 horas)
            current_time += timedelta(minutes=random.randint(30, 120))

    db.session.commit()
    print(f"✅ {readings_created} leituras criadas!")


def create_alerts():
    """Cria alertas históricos."""
    print("🚨 Criando alertas...")

    farms = Fazenda.query.all()
    alert_types = ['Chuva Intensa', 'Temperatura Extrema', 'Vento Forte', 'Umidade Crítica', 'Falha de Sensor']
    intensities = ['Leve', 'Moderado', 'Severo', 'Critico']

    alerts_created = 0

    # Criar alertas para os últimos 30 dias
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)

    for farm in farms:
        current_time = start_time

        while current_time <= end_time:
            # Probabilidade de alerta (5% por dia)
            if random.random() < 0.05:
                alert_type = random.choice(alert_types)
                intensity = random.choice(intensities)

                # Probabilidade baseada na intensidade
                if intensity == 'Critico':
                    probability = random.uniform(85, 95)
                elif intensity == 'Severo':
                    probability = random.uniform(70, 85)
                elif intensity == 'Moderado':
                    probability = random.uniform(50, 70)
                else:
                    probability = random.uniform(25, 50)

                # Mensagens baseadas no tipo
                messages = {
                    'Chuva Intensa': f'Previsão de chuva intensa com {probability:.1f}% de probabilidade',
                    'Temperatura Extrema': f'Temperatura extrema detectada - {probability:.1f}% de confiança',
                    'Vento Forte': f'Rajadas de vento forte previstas - {probability:.1f}% de probabilidade',
                    'Umidade Crítica': f'Níveis críticos de umidade - {probability:.1f}% de certeza',
                    'Falha de Sensor': f'Possível falha em sensor detectada - {probability:.1f}% de confiança'
                }

                alert = Alerta(
                    id_fazenda=farm.id_fazenda,
                    timestamp_emissao=current_time,
                    tipo_alerta=alert_type,
                    intensidade=intensity,
                    probabilidade=round(probability, 2),
                    mensagem=messages[alert_type],
                    status='Ativo' if current_time > end_time - timedelta(hours=6) else random.choice(['Reconhecido', 'Resolvido'])
                )

                # Se foi reconhecido, adicionar timestamp
                if alert.status in ['Reconhecido', 'Resolvido']:
                    alert.timestamp_reconhecimento = current_time + timedelta(minutes=random.randint(10, 180))
                    alert.id_usuario_reconheceu = random.randint(1, 4)  # Assumindo IDs de usuário de 1 a 4

                db.session.add(alert)
                alerts_created += 1

            current_time += timedelta(hours=random.randint(6, 24))

    db.session.commit()
    print(f"✅ {alerts_created} alertas criados!")


def create_actuator_commands():
    """Cria registros de comandos de atuadores."""
    print("🎛️  Criando registros de comandos...")

    actuators = Atuador.query.all()
    commands = ['LIGAR', 'DESLIGAR', 'STATUS', 'RESET', 'CONFIGURAR']

    commands_created = 0

    # Criar comandos para os últimos 15 dias
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=15)

    for actuator in actuators:
        current_time = start_time

        while current_time <= end_time:
            # Probabilidade de comando (10% por dia)
            if random.random() < 0.1:
                command = random.choice(commands)

                # Status de execução
                status = random.choices(
                    ['Sucesso', 'Falha', 'Pendente'],
                    weights=[85, 10, 5]
                )[0]

                # Parâmetros baseados no comando
                parameters = {}
                if command == 'CONFIGURAR':
                    parameters = {'intensidade': random.randint(1, 10), 'modo': random.choice(['auto', 'manual'])}
                elif command in ['LIGAR', 'DESLIGAR']:
                    parameters = {'duracao_segundos': random.randint(300, 3600)}

                # Mensagem de retorno
                if status == 'Sucesso':
                    return_message = f"Comando {command} executado com sucesso"
                elif status == 'Falha':
                    return_message = f"Falha ao executar {command}: {random.choice(['Timeout', 'Conexão perdida', 'Erro interno'])}"
                else:
                    return_message = f"Comando {command} em execução..."

                command_record = RegistroComandoAtuador(
                    id_atuador=actuator.id_atuador,
                    id_usuario_executor=random.randint(1, 4),
                    comando_executado=command,
                    parametros_comando=parameters,
                    timestamp_comando=current_time,
                    status_execucao=status,
                    mensagem_retorno=return_message
                )

                db.session.add(command_record)
                commands_created += 1

            current_time += timedelta(hours=random.randint(4, 48))

    db.session.commit()
    print(f"✅ {commands_created} registros de comandos criados!")


def main():
    """Função principal."""
    print("🌱 StormGuard - Populador de Dados de Demonstração")
    print("=" * 50)

    # Criar aplicação Flask
    app = create_app('development')

    with app.app_context():
        print("🔄 Conectando ao banco de dados...")

        # Limpar dados existentes
        if input("⚠️  Deseja limpar todos os dados existentes? (s/N): ").lower().startswith('s'):
            clear_database()

        # Criar todas as tabelas
        db.create_all()

        # Popular com dados
        try:
            create_access_levels()
            create_users()
            create_farms()
            create_sensor_types()
            create_actuator_types()
            create_devices()
            create_sensors()
            create_actuators()
            create_sensor_readings()
            create_alerts()
            create_actuator_commands()

            print("\n" + "=" * 50)
            print("🎉 Dados de demonstração criados com sucesso!")
            print("\n📋 Resumo:")
            print(f"   👥 Usuários: {Usuario.query.count()}")
            print(f"   🚜 Fazendas: {Fazenda.query.count()}")
            print(f"   📡 Dispositivos: {Dispositivo.query.count()}")
            print(f"   🔬 Sensores: {Sensor.query.count()}")
            print(f"   ⚙️  Atuadores: {Atuador.query.count()}")
            print(f"   📊 Leituras: {RegistroLeitura.query.count()}")
            print(f"   🚨 Alertas: {Alerta.query.count()}")
            print(f"   🎛️  Comandos: {RegistroComandoAtuador.query.count()}")

            print("\n🔑 Credenciais de acesso:")
            print("   Admin: admin / admin123")
            print("   Usuário: joao.silva / joao123")
            print("   Usuário: maria.santos / maria123")
            print("   Usuário: carlos.oliveira / carlos123")

            print("\n✨ Sistema pronto para demonstração!")

        except Exception as e:
            print(f"❌ Erro ao criar dados: {e}")
            db.session.rollback()
            return 1

    return 0


if __name__ == '__main__':
    exit(main())
