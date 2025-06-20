#!/usr/bin/env python3
"""
Script para configurar o banco de dados e inserir dados iniciais.
Execute este script após criar as tabelas no banco de dados.

Uso:
    python setup_database.py
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    Usuario, NivelAcesso, Fazenda, Dispositivo, TipoSensor,
    TipoAtuador, Sensor, Atuador
)

def criar_dados_iniciais():
    """Cria dados iniciais necessários para o funcionamento do sistema."""

    print("🌱 Criando dados iniciais...")

    # 1. Criar níveis de acesso
    print("📋 Criando níveis de acesso...")
    niveis_acesso = [
        {'nome_nivel': 'Administrador', 'descricao': 'Acesso completo ao sistema'},
        {'nome_nivel': 'Gerente', 'descricao': 'Gerenciamento de fazenda e usuários'},
        {'nome_nivel': 'Operador', 'descricao': 'Operação e monitoramento'},
        {'nome_nivel': 'Visualizador', 'descricao': 'Apenas visualização de dados'}
    ]

    for nivel_data in niveis_acesso:
        if not NivelAcesso.query.filter_by(nome_nivel=nivel_data['nome_nivel']).first():
            nivel = NivelAcesso(**nivel_data)
            db.session.add(nivel)
            print(f"   ✅ Nível '{nivel_data['nome_nivel']}' criado")

    # 2. Criar usuário administrador padrão
    print("👤 Criando usuário administrador...")
    if not Usuario.query.filter_by(nome_usuario='admin').first():
        admin = Usuario(
            nome_usuario='admin',
            nome_completo='Administrador do Sistema',
            email='admin@stormguard.com.br',
            status_conta='Ativa'
        )
        admin.set_password('admin123')  # ALTERE ESTA SENHA EM PRODUÇÃO!
        db.session.add(admin)
        print("   ✅ Usuário administrador criado (login: admin, senha: admin123)")
        print("   ⚠️  IMPORTANTE: Altere a senha padrão em produção!")

    # 3. Criar fazenda de demonstração
    print("🚜 Criando fazenda de demonstração...")
    if not Fazenda.query.filter_by(nome_fazenda='Fazenda Demonstração').first():
        fazenda = Fazenda(
            nome_fazenda='Fazenda Demonstração',
            localizacao_latitude=-23.5505,
            localizacao_longitude=-46.6333,
            area_total_hectares=100.50,
            descricao='Fazenda para testes e demonstração do sistema StormGuard'
        )
        db.session.add(fazenda)
        print("   ✅ Fazenda 'Fazenda Demonstração' criada")

    # 4. Criar tipos de sensores
    print("🔬 Criando tipos de sensores...")
    tipos_sensores = [
        {'nome_tipo': 'temperatura', 'unidade_medida': '°C', 'descricao': 'Sensor de temperatura ambiente'},
        {'nome_tipo': 'umidade', 'unidade_medida': '%', 'descricao': 'Sensor de umidade relativa do ar'},
        {'nome_tipo': 'pressao', 'unidade_medida': 'hPa', 'descricao': 'Sensor de pressão atmosférica'},
        {'nome_tipo': 'precipitacao', 'unidade_medida': 'mm', 'descricao': 'Sensor de precipitação (chuva)'},
        {'nome_tipo': 'velocidade_vento', 'unidade_medida': 'm/s', 'descricao': 'Sensor de velocidade do vento'},
        {'nome_tipo': 'direcao_vento', 'unidade_medida': '°', 'descricao': 'Sensor de direção do vento'},
        {'nome_tipo': 'radiacao_solar', 'unidade_medida': 'W/m²', 'descricao': 'Sensor de radiação solar'},
        {'nome_tipo': 'ph_solo', 'unidade_medida': 'pH', 'descricao': 'Sensor de pH do solo'},
        {'nome_tipo': 'campo_eletrico', 'unidade_medida': 'V/m', 'descricao': 'Sensor de campo elétrico atmosférico'},
        {'nome_tipo': 'nivel_agua', 'unidade_medida': 'cm', 'descricao': 'Sensor de nível de água'}
    ]

    for tipo_data in tipos_sensores:
        if not TipoSensor.query.filter_by(nome_tipo=tipo_data['nome_tipo']).first():
            tipo = TipoSensor(**tipo_data)
            db.session.add(tipo)
            print(f"   ✅ Tipo de sensor '{tipo_data['nome_tipo']}' criado")

    # 5. Criar tipos de atuadores
    print("⚙️ Criando tipos de atuadores...")
    tipos_atuadores = [
        {'nome_tipo': 'Irrigação'},
        {'nome_tipo': 'Ventilação'},
        {'nome_tipo': 'Aquecimento'},
        {'nome_tipo': 'Iluminação'},
        {'nome_tipo': 'Bomba de Água'},
        {'nome_tipo': 'Válvula Solenoide'},
        {'nome_tipo': 'Sistema de Alerta'}
    ]

    for tipo_data in tipos_atuadores:
        if not TipoAtuador.query.filter_by(nome_tipo=tipo_data['nome_tipo']).first():
            tipo = TipoAtuador(**tipo_data)
            db.session.add(tipo)
            print(f"   ✅ Tipo de atuador '{tipo_data['nome_tipo']}' criado")

    # Commit das operações básicas
    try:
        db.session.commit()
        print("💾 Dados básicos salvos com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao salvar dados básicos: {e}")
        return False

    # 6. Criar dispositivos de demonstração
    print("📡 Criando dispositivos de demonstração...")
    fazenda = Fazenda.query.filter_by(nome_fazenda='Fazenda Demonstração').first()

    if fazenda:
        dispositivos_demo = [
            {
                'identificador_unico': 'sensor_area_central_01',
                'nome_amigavel': 'Estação Meteorológica Central',
                'area': 'Central',
                'id_fazenda': fazenda.id_fazenda
            },
            {
                'identificador_unico': 'sensor_area_norte_01',
                'nome_amigavel': 'Sensor da Estufa Norte',
                'area': 'Norte',
                'id_fazenda': fazenda.id_fazenda
            },
            {
                'identificador_unico': 'sensor_area_sul_01',
                'nome_amigavel': 'Monitor do Campo Sul',
                'area': 'Sul',
                'id_fazenda': fazenda.id_fazenda
            }
        ]

        for disp_data in dispositivos_demo:
            if not Dispositivo.query.filter_by(identificador_unico=disp_data['identificador_unico']).first():
                dispositivo = Dispositivo(**disp_data)
                db.session.add(dispositivo)
                print(f"   ✅ Dispositivo '{disp_data['nome_amigavel']}' criado")

    # 7. Associar sensores aos dispositivos
    print("🔗 Associando sensores aos dispositivos...")

    # Configurações de sensores por dispositivo
    configuracao_sensores = {
        'sensor_area_central_01': ['temperatura', 'umidade', 'pressao', 'precipitacao', 'velocidade_vento', 'campo_eletrico'],
        'sensor_area_norte_01': ['temperatura', 'umidade', 'ph_solo'],
        'sensor_area_sul_01': ['temperatura', 'umidade', 'nivel_agua']
    }

    for identificador, tipos_sensor in configuracao_sensores.items():
        dispositivo = Dispositivo.query.filter_by(identificador_unico=identificador).first()
        if not dispositivo:
            continue

        for nome_tipo in tipos_sensor:
            tipo_sensor = TipoSensor.query.filter_by(nome_tipo=nome_tipo).first()
            if not tipo_sensor:
                continue

            # Verifica se o sensor já existe
            sensor_existente = Sensor.query.filter_by(
                id_dispositivo=dispositivo.id_dispositivo,
                id_tipo_sensor=tipo_sensor.id_tipo_sensor
            ).first()

            if not sensor_existente:
                sensor = Sensor(
                    id_dispositivo=dispositivo.id_dispositivo,
                    id_tipo_sensor=tipo_sensor.id_tipo_sensor,
                    status='Ativo'
                )
                db.session.add(sensor)
                print(f"   ✅ Sensor '{nome_tipo}' associado ao dispositivo '{identificador}'")

    # 8. Criar alguns atuadores de exemplo
    print("🤖 Criando atuadores de demonstração...")
    if fazenda:
        atuadores_demo = [
            {
                'nome_atuador': 'Sistema de Irrigação Central',
                'id_tipo_atuador': TipoAtuador.query.filter_by(nome_tipo='Irrigação').first().id_tipo_atuador,
                'id_fazenda': fazenda.id_fazenda,
                'status_atual': 'Desligado',
                'endereco_logico': 'central_irrig_01'
            },
            {
                'nome_atuador': 'Bomba de Água do Poço',
                'id_tipo_atuador': TipoAtuador.query.filter_by(nome_tipo='Bomba de Água').first().id_tipo_atuador,
                'id_fazenda': fazenda.id_fazenda,
                'status_atual': 'Desligado',
                'endereco_logico': 'bomba_poco_01'
            }
        ]

        for atu_data in atuadores_demo:
            if not Atuador.query.filter_by(nome_atuador=atu_data['nome_atuador']).first():
                atuador = Atuador(**atu_data)
                db.session.add(atuador)
                print(f"   ✅ Atuador '{atu_data['nome_atuador']}' criado")

    # Commit final
    try:
        db.session.commit()
        print("💾 Todos os dados de demonstração salvos com sucesso!")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao salvar dados de demonstração: {e}")
        return False

def verificar_estrutura_banco():
    """Verifica se as tabelas existem no banco de dados."""
    print("🔍 Verificando estrutura do banco de dados...")

    try:
        # Testa se consegue consultar uma tabela essencial
        Usuario.query.first()
        print("   ✅ Tabelas encontradas no banco de dados")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco de dados: {e}")
        print("   💡 Execute primeiro: flask db upgrade")
        return False

def main():
    """Função principal do script."""
    print("🚀 StormGuard - Setup do Banco de Dados")
    print("=" * 50)

    # Cria a aplicação Flask
    app = create_app('development')

    with app.app_context():
        # Verifica se o banco existe
        if not verificar_estrutura_banco():
            print("\n❌ Setup interrompido. Configure o banco de dados primeiro.")
            return False

        # Cria os dados iniciais
        if criar_dados_iniciais():
            print("\n🎉 Setup concluído com sucesso!")
            print("\n📋 Resumo:")
            print(f"   • Usuários: {Usuario.query.count()}")
            print(f"   • Fazendas: {Fazenda.query.count()}")
            print(f"   • Dispositivos: {Dispositivo.query.count()}")
            print(f"   • Tipos de Sensores: {TipoSensor.query.count()}")
            print(f"   • Sensores: {Sensor.query.count()}")
            print(f"   • Tipos de Atuadores: {TipoAtuador.query.count()}")
            print(f"   • Atuadores: {Atuador.query.count()}")

            print("\n🔑 Credenciais de acesso:")
            print("   Login: admin")
            print("   Senha: admin123")
            print("   ⚠️  Altere a senha após o primeiro login!")

            print("\n📡 Dispositivos MQTT configurados:")
            for dispositivo in Dispositivo.query.all():
                sensores = [s.tipo_sensor.nome_tipo for s in dispositivo.sensores]
                print(f"   • {dispositivo.identificador_unico} - {len(sensores)} sensores")

            return True
        else:
            print("\n❌ Falha no setup. Verifique os erros acima.")
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
