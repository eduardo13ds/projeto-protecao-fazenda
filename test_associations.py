#!/usr/bin/env python3
"""
Script para testar as associações entre dispositivos e sensores.
Verifica se o sistema está funcionando corretamente.

Uso:
    python test_associations.py
"""

import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    Dispositivo, Sensor, TipoSensor, RegistroLeitura, Fazenda
)
from app.mqtt.client import mqtt_client, SENSOR_MAP, DEVICE_MAP

def testar_modelos():
    """Testa os modelos e relacionamentos."""
    print("🧪 Testando modelos e relacionamentos...")

    try:
        # Teste 1: Verificar se existem dispositivos
        total_dispositivos = Dispositivo.query.count()
        print(f"   📱 Total de dispositivos: {total_dispositivos}")

        if total_dispositivos == 0:
            print("   ⚠️  Nenhum dispositivo encontrado. Execute setup_database.py primeiro.")
            return False

        # Teste 2: Verificar sensores associados
        total_sensores = Sensor.query.count()
        print(f"   🔬 Total de sensores: {total_sensores}")

        # Teste 3: Verificar relacionamentos
        for dispositivo in Dispositivo.query.all():
            sensores_count = dispositivo.sensores.count()
            tipos_disponiveis = len(dispositivo.tipos_sensores_disponiveis)

            print(f"   📡 {dispositivo.identificador_unico}:")
            print(f"      - Nome: {dispositivo.nome_amigavel}")
            print(f"      - Sensores associados: {sensores_count}")
            print(f"      - Tipos disponíveis para associar: {tipos_disponiveis}")
            print(f"      - Status: {dispositivo.status}")
            print(f"      - Online: {'✅' if dispositivo.esta_online else '❌'}")

            # Lista sensores do dispositivo
            for sensor in dispositivo.sensores:
                print(f"        • {sensor.tipo_sensor.nome_tipo} ({sensor.tipo_sensor.unidade_medida}) - {sensor.status}")

        return True

    except Exception as e:
        print(f"   ❌ Erro ao testar modelos: {e}")
        return False

def testar_mapa_mqtt():
    """Testa o mapeamento MQTT."""
    print("\n🌐 Testando mapeamento MQTT...")

    try:
        # Força reload do mapa
        mqtt_client.reload_sensor_map()

        print(f"   📊 Dispositivos no mapa MQTT: {len(DEVICE_MAP)}")
        print(f"   📊 Sensores no mapa MQTT: {sum(len(sensors) for sensors in SENSOR_MAP.values())}")

        # Verifica consistência entre banco e mapa MQTT
        dispositivos_db = set(d.identificador_unico for d in Dispositivo.query.filter_by(status='Ativo').all())
        dispositivos_mqtt = set(DEVICE_MAP.keys())

        print(f"   🔍 Dispositivos no banco: {len(dispositivos_db)}")
        print(f"   🔍 Dispositivos no MQTT: {len(dispositivos_mqtt)}")

        # Dispositivos que estão no banco mas não no MQTT
        ausentes_mqtt = dispositivos_db - dispositivos_mqtt
        if ausentes_mqtt:
            print(f"   ⚠️  Dispositivos no banco mas não no MQTT: {ausentes_mqtt}")

        # Dispositivos que estão no MQTT mas não no banco
        ausentes_db = dispositivos_mqtt - dispositivos_db
        if ausentes_db:
            print(f"   ⚠️  Dispositivos no MQTT mas não no banco: {ausentes_db}")

        # Detalhes do mapeamento
        for device_id, device_info in DEVICE_MAP.items():
            sensores_info = device_info.get('sensores', {})
            print(f"   📡 {device_id}:")
            print(f"      - ID DB: {device_info.get('id_dispositivo')}")
            print(f"      - Nome: {device_info.get('nome_amigavel')}")
            print(f"      - Área: {device_info.get('area')}")
            print(f"      - Sensores: {len(sensores_info)}")

            for sensor_type, sensor_info in sensores_info.items():
                print(f"        • {sensor_type}: ID {sensor_info['id_sensor']} ({sensor_info['unidade_medida']})")

        return len(ausentes_mqtt) == 0 and len(ausentes_db) == 0

    except Exception as e:
        print(f"   ❌ Erro ao testar mapa MQTT: {e}")
        return False

def testar_associacao_manual():
    """Testa associação manual de sensores."""
    print("\n🔧 Testando associação manual de sensores...")

    try:
        # Pega o primeiro dispositivo que tem tipos disponíveis
        dispositivo = None
        for d in Dispositivo.query.all():
            if len(d.tipos_sensores_disponiveis) > 0:
                dispositivo = d
                break

        if not dispositivo:
            print("   ℹ️  Todos os dispositivos já têm todos os tipos de sensores associados.")
            return True

        # Pega o primeiro tipo disponível
        tipo_disponivel = dispositivo.tipos_sensores_disponiveis[0]
        print(f"   🎯 Testando associação de '{tipo_disponivel.nome_tipo}' ao dispositivo '{dispositivo.identificador_unico}'...")

        # Conta sensores antes
        sensores_antes = dispositivo.sensores.count()

        # Associa o sensor
        novo_sensor = dispositivo.associar_sensor(tipo_disponivel.id_tipo_sensor)

        if novo_sensor:
            print(f"   ✅ Sensor associado com sucesso: ID {novo_sensor.id_sensor}")

            # Salva no banco
            db.session.commit()

            # Verifica se aumentou
            sensores_depois = dispositivo.sensores.count()
            print(f"   📊 Sensores antes: {sensores_antes}, depois: {sensores_depois}")

            # Recarrega mapa MQTT
            mqtt_client.reload_sensor_map()

            # Verifica se apareceu no mapa
            device_sensors = SENSOR_MAP.get(dispositivo.identificador_unico, {})
            sensor_no_mapa = tipo_disponivel.nome_tipo.lower() in device_sensors
            print(f"   🗺️  Sensor apareceu no mapa MQTT: {'✅' if sensor_no_mapa else '❌'}")

            # Remove o sensor para não bagunçar os testes
            print(f"   🧹 Removendo sensor de teste...")
            sucesso, msg = dispositivo.desassociar_sensor(novo_sensor.id_sensor)
            if sucesso:
                db.session.commit()
                mqtt_client.reload_sensor_map()
                print(f"   ✅ {msg}")
            else:
                print(f"   ⚠️  {msg}")

            return True
        else:
            print("   ❌ Falha ao associar sensor")
            return False

    except Exception as e:
        print(f"   ❌ Erro ao testar associação manual: {e}")
        db.session.rollback()
        return False

def testar_simulacao_mqtt():
    """Simula uma mensagem MQTT para testar o processamento."""
    print("\n📡 Testando simulação de mensagem MQTT...")

    try:
        # Pega um dispositivo com sensores
        dispositivo = Dispositivo.query.filter(Dispositivo.sensores.any()).first()

        if not dispositivo:
            print("   ⚠️  Nenhum dispositivo com sensores encontrado.")
            return False

        print(f"   🎯 Usando dispositivo: {dispositivo.identificador_unico}")

        # Conta leituras antes
        leituras_antes = RegistroLeitura.query.count()

        # Prepara dados simulados
        dados_simulados = {'device_id': dispositivo.identificador_unico}

        # Adiciona valores para cada sensor do dispositivo
        for sensor in dispositivo.sensores:
            tipo_nome = sensor.tipo_sensor.nome_tipo.lower()
            # Valores simulados baseados no tipo
            valores_exemplo = {
                'temperatura': 25.5,
                'umidade': 65.0,
                'pressao': 1013.25,
                'precipitacao': 0.0,
                'velocidade_vento': 3.2,
                'campo_eletrico': 120.5,
                'ph_solo': 6.8,
                'nivel_agua': 45.2
            }

            valor = valores_exemplo.get(tipo_nome, 10.0)
            dados_simulados[tipo_nome] = valor
            print(f"      • {tipo_nome}: {valor} {sensor.tipo_sensor.unidade_medida}")

        print(f"   📤 Simulando envio de dados: {dados_simulados}")

        # Simula o processamento MQTT
        with mqtt_client.app.app_context():
            sucesso = mqtt_client._save_data_to_db(dados_simulados.copy())

        if sucesso:
            print("   ✅ Dados processados com sucesso")

            # Verifica se aumentaram as leituras
            leituras_depois = RegistroLeitura.query.count()
            leituras_criadas = leituras_depois - leituras_antes
            print(f"   📊 Leituras criadas: {leituras_criadas}")

            # Mostra algumas leituras recentes
            leituras_recentes = RegistroLeitura.query.order_by(RegistroLeitura.timestamp_leitura.desc()).limit(3).all()
            print("   📋 Últimas leituras criadas:")
            for leitura in leituras_recentes:
                sensor_nome = leitura.sensor.tipo_sensor.nome_tipo if leitura.sensor else "Unknown"
                print(f"      • {sensor_nome}: {leitura.valor_leitura} (Qualidade: {leitura.qualidade})")

            return True
        else:
            print("   ❌ Falha ao processar dados")
            return False

    except Exception as e:
        print(f"   ❌ Erro ao testar simulação MQTT: {e}")
        return False

def testar_consultas_otimizadas():
    """Testa consultas otimizadas."""
    print("\n⚡ Testando consultas otimizadas...")

    try:
        # Teste de performance de consultas
        start_time = datetime.now()

        # Consulta com joins otimizados
        resultado = db.session.query(
            Dispositivo.identificador_unico,
            Dispositivo.nome_amigavel,
            TipoSensor.nome_tipo,
            Sensor.status
        ).join(
            Sensor, Dispositivo.id_dispositivo == Sensor.id_dispositivo
        ).join(
            TipoSensor, Sensor.id_tipo_sensor == TipoSensor.id_tipo_sensor
        ).filter(
            Dispositivo.status == 'Ativo'
        ).all()

        end_time = datetime.now()
        tempo_consulta = (end_time - start_time).total_seconds()

        print(f"   ⏱️  Consulta executada em {tempo_consulta:.3f}s")
        print(f"   📊 Registros retornados: {len(resultado)}")

        # Teste de consulta de leituras recentes
        if RegistroLeitura.query.count() > 0:
            start_time = datetime.now()

            leituras_recentes = RegistroLeitura.query.join(
                Sensor
            ).join(
                TipoSensor
            ).filter(
                RegistroLeitura.timestamp_leitura >= datetime.now() - timedelta(hours=24)
            ).order_by(
                RegistroLeitura.timestamp_leitura.desc()
            ).limit(10).all()

            end_time = datetime.now()
            tempo_leituras = (end_time - start_time).total_seconds()

            print(f"   ⏱️  Consulta de leituras em {tempo_leituras:.3f}s")
            print(f"   📊 Leituras nas últimas 24h: {len(leituras_recentes)}")

        return True

    except Exception as e:
        print(f"   ❌ Erro ao testar consultas: {e}")
        return False

def main():
    """Função principal do script."""
    print("🧪 StormGuard - Teste de Associações")
    print("=" * 50)

    # Cria a aplicação Flask
    app = create_app('development')

    resultados = []

    with app.app_context():
        # Executa todos os testes
        testes = [
            ("Modelos e Relacionamentos", testar_modelos),
            ("Mapeamento MQTT", testar_mapa_mqtt),
            ("Associação Manual", testar_associacao_manual),
            ("Simulação MQTT", testar_simulacao_mqtt),
            ("Consultas Otimizadas", testar_consultas_otimizadas)
        ]

        for nome_teste, funcao_teste in testes:
            print(f"\n{'='*20} {nome_teste} {'='*20}")
            try:
                sucesso = funcao_teste()
                resultados.append((nome_teste, sucesso))
            except Exception as e:
                print(f"❌ Erro inesperado no teste '{nome_teste}': {e}")
                resultados.append((nome_teste, False))

    # Resumo dos resultados
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)

    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{nome:.<40} {status}")
        if sucesso:
            sucessos += 1

    print(f"\n🎯 Resultado: {sucessos}/{len(resultados)} testes passaram")

    if sucessos == len(resultados):
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os problemas acima.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
