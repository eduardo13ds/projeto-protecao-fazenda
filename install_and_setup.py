#!/usr/bin/env python3
"""
Script simples para configurar o ambiente e banco de dados do StormGuard.
Execute este script primeiro para configurar tudo automaticamente.

Uso:
    python install_and_setup.py
"""

import sys
import os
import subprocess

def executar_script_sql():
    """Executa comandos SQL diretamente no MySQL."""
    print("🗄️  Configurando banco de dados MySQL...")

    try:
        import mysql.connector
        from mysql.connector import Error

        # Configurações do banco
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': ''
        }

        # Conecta ao MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Cria o banco
        cursor.execute("CREATE DATABASE IF NOT EXISTS stormguard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE stormguard")

        print("   ✅ Banco 'stormguard' criado/verificado")

        # Cria as tabelas essenciais
        tabelas_sql = [
            """
            CREATE TABLE IF NOT EXISTS fazendas (
                ID_Fazenda INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Fazenda VARCHAR(100) NOT NULL,
                Localizacao_Latitude DECIMAL(10, 8),
                Localizacao_Longitude DECIMAL(11, 8),
                Area_Total_Hectares DECIMAL(10, 2),
                Descricao TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE IF NOT EXISTS dispositivos (
                ID_Dispositivo INT AUTO_INCREMENT PRIMARY KEY,
                Identificador_Unico VARCHAR(80) NOT NULL UNIQUE,
                Nome_Amigavel VARCHAR(100),
                Area VARCHAR(50),
                ID_Fazenda INT NOT NULL,
                Status ENUM('Ativo', 'Inativo', 'Manutencao') DEFAULT 'Ativo',
                Data_Instalacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Ultimo_Ping TIMESTAMP NULL,
                Versao_Firmware VARCHAR(20),
                Observacoes TEXT,
                FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda),
                INDEX idx_identificador (Identificador_Unico)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE IF NOT EXISTS tipos_sensor (
                ID_Tipo_Sensor INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Tipo VARCHAR(50) NOT NULL UNIQUE,
                Unidade_Medida VARCHAR(20),
                Descricao TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE IF NOT EXISTS sensores (
                ID_Sensor INT AUTO_INCREMENT PRIMARY KEY,
                ID_Dispositivo INT NOT NULL,
                ID_Tipo_Sensor INT NOT NULL,
                Status ENUM('Ativo', 'Inativo', 'Manutencao') DEFAULT 'Ativo',
                Ultima_Leitura TIMESTAMP NULL,
                Limite_Minimo_Alerta DECIMAL(10, 4),
                Limite_Maximo_Alerta DECIMAL(10, 4),
                FOREIGN KEY (ID_Dispositivo) REFERENCES dispositivos(ID_Dispositivo) ON DELETE CASCADE,
                FOREIGN KEY (ID_Tipo_Sensor) REFERENCES tipos_sensor(ID_Tipo_Sensor),
                UNIQUE KEY unique_device_sensor (ID_Dispositivo, ID_Tipo_Sensor)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE IF NOT EXISTS registro_leituras (
                ID_Leitura BIGINT AUTO_INCREMENT PRIMARY KEY,
                ID_Sensor INT NOT NULL,
                Valor_Leitura VARCHAR(255) NOT NULL,
                Timestamp_Leitura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Qualidade ENUM('Confiavel', 'Ruido', 'Fora da Faixa') DEFAULT 'Confiavel',
                Valor_Numerico DECIMAL(15, 6),
                Unidade_Medida VARCHAR(20),
                Observacoes TEXT,
                FOREIGN KEY (ID_Sensor) REFERENCES sensores(ID_Sensor) ON DELETE CASCADE,
                INDEX idx_sensor_timestamp (ID_Sensor, Timestamp_Leitura)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE IF NOT EXISTS usuarios (
                ID_Usuario INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Usuario VARCHAR(50) NOT NULL UNIQUE,
                Senha_Hash VARCHAR(255) NOT NULL,
                Nome_Completo VARCHAR(100),
                Email VARCHAR(100) NOT NULL UNIQUE,
                Status_Conta ENUM('Ativa', 'Inativa', 'Bloqueada') DEFAULT 'Ativa',
                Data_Criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Ultimo_Login TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        ]

        for sql in tabelas_sql:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Tabelas principais criadas")

        # Dados iniciais
        dados_iniciais = [
            """
            INSERT IGNORE INTO fazendas (Nome_Fazenda, Localizacao_Latitude, Localizacao_Longitude, Area_Total_Hectares, Descricao) VALUES
            ('Fazenda Demonstração', -23.5505, -46.6333, 100.50, 'Fazenda para testes e demonstração')
            """,

            """
            INSERT IGNORE INTO tipos_sensor (Nome_Tipo, Unidade_Medida, Descricao) VALUES
            ('temperatura', '°C', 'Sensor de temperatura'),
            ('umidade', '%', 'Sensor de umidade'),
            ('pressao', 'hPa', 'Sensor de pressão'),
            ('campo_eletrico', 'V/m', 'Sensor de campo elétrico')
            """,

            """
            INSERT IGNORE INTO usuarios (Nome_Usuario, Senha_Hash, Nome_Completo, Email) VALUES
            ('admin', 'pbkdf2:sha256:600000$M9xJQQKV$f67de0a7c17bb8bd65b17edc2dd9b47e9e6e1c0ac2ebc95c30b75a5ab0c93b2e', 'Administrador', 'admin@stormguard.com')
            """,

            """
            INSERT IGNORE INTO dispositivos (Identificador_Unico, Nome_Amigavel, Area, ID_Fazenda) VALUES
            ('sensor_area_central_01', 'Estação Central', 'Central', 1),
            ('sensor_area_norte_01', 'Sensor Norte', 'Norte', 1)
            """
        ]

        for sql in dados_iniciais:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Dados iniciais inseridos")

        # Associa alguns sensores aos dispositivos
        cursor.execute("""
            INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor)
            SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor
            FROM dispositivos d, tipos_sensor ts
            WHERE d.Identificador_Unico = 'sensor_area_central_01'
            AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'campo_eletrico')
        """)

        cursor.execute("""
            INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor)
            SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor
            FROM dispositivos d, tipos_sensor ts
            WHERE d.Identificador_Unico = 'sensor_area_norte_01'
            AND ts.Nome_Tipo IN ('temperatura', 'umidade')
        """)

        connection.commit()
        print("   ✅ Sensores associados aos dispositivos")

        cursor.close()
        connection.close()

        return True

    except ImportError:
        print("   ❌ mysql-connector-python não instalado. Execute 'pip install mysql-connector-python'")
        return False
    except Error as e:
        print(f"   ❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def verificar_estrutura():
    """Verifica se a estrutura foi criada corretamente."""
    print("🔍 Verificando estrutura do banco...")

    try:
        import mysql.connector

        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='stormguard'
        )

        cursor = connection.cursor()

        # Verifica tabelas
        cursor.execute("SHOW TABLES")
        tabelas = [t[0] for t in cursor.fetchall()]
        print(f"   📊 Tabelas criadas: {len(tabelas)}")

        # Verifica dispositivos
        cursor.execute("SELECT COUNT(*) FROM dispositivos")
        total_dispositivos = cursor.fetchone()[0]
        print(f"   📱 Dispositivos: {total_dispositivos}")

        # Verifica sensores
        cursor.execute("SELECT COUNT(*) FROM sensores")
        total_sensores = cursor.fetchone()[0]
        print(f"   🔬 Sensores: {total_sensores}")

        # Verifica estrutura específica das tabelas críticas
        cursor.execute("DESCRIBE dispositivos")
        colunas_dispositivos = [col[0] for col in cursor.fetchall()]
        if 'ID_Dispositivo' in colunas_dispositivos:
            print("   ✅ Tabela dispositivos está correta")
        else:
            print("   ❌ Tabela dispositivos com problema")

        cursor.execute("DESCRIBE sensores")
        colunas_sensores = [col[0] for col in cursor.fetchall()]
        if 'ID_Dispositivo' in colunas_sensores and 'ID_Sensor' in colunas_sensores:
            print("   ✅ Tabela sensores está correta")
        else:
            print("   ❌ Tabela sensores com problema")

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 StormGuard - Instalação e Configuração Automática")
    print("=" * 60)

    print("ℹ️  Este script irá:")
    print("   • Instalar dependências Python")
    print("   • Criar banco de dados MySQL")
    print("   • Criar tabelas necessárias")
    print("   • Inserir dados de demonstração")
    print()

    resposta = input("Continuar? (s/N): ").lower().strip()
    if resposta != 's':
        print("❌ Operação cancelada")
        return False

    print()

    # Passo 1: Instalar dependências
    if not instalar_dependencias():
        print("❌ Falha na instalação das dependências")
        return False

    print()

    # Passo 2: Configurar banco
    if not executar_script_sql():
        print("❌ Falha na configuração do banco")
        return False

    print()

    # Passo 3: Verificar
    if not verificar_estrutura():
        print("⚠️  Estrutura pode ter problemas")

    print("\n🎉 Configuração concluída com sucesso!")
    print("\n📋 Informações importantes:")
    print("   • Banco: stormguard")
    print("   • Login: admin")
    print("   • Senha: admin123")
    print("   • Dispositivos de teste criados")

    print("\n🚀 Próximos passos:")
    print("   1. Execute o Flask: flask run")
    print("   2. Acesse: http://localhost:5000")
    print("   3. Faça login com admin/admin123")
    print("   4. Vá em /admin para gerenciar dispositivos")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
