#!/usr/bin/env python3
"""
Script simplificado para configurar apenas o banco de dados MySQL do StormGuard.
As dependências devem estar já instaladas.

Uso:
    python setup_banco_simples.py
"""

import sys
import os

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

        # Primeiro, remove as tabelas se existirem (ordem inversa das foreign keys)
        print("   🗑️  Removendo tabelas existentes...")

        drop_tables = [
            "DROP TABLE IF EXISTS documentos_verificados",
            "DROP TABLE IF EXISTS usuario_fazenda_acesso",
            "DROP TABLE IF EXISTS registro_comandos_atuadores",
            "DROP TABLE IF EXISTS alertas",
            "DROP TABLE IF EXISTS atuadores",
            "DROP TABLE IF EXISTS tipos_atuador",
            "DROP TABLE IF EXISTS registro_leituras",
            "DROP TABLE IF EXISTS sensores",
            "DROP TABLE IF EXISTS tipos_sensor",
            "DROP TABLE IF EXISTS dispositivos",
            "DROP TABLE IF EXISTS fazendas",
            "DROP TABLE IF EXISTS usuarios",
            "DROP TABLE IF EXISTS niveis_acesso"
        ]

        for drop_sql in drop_tables:
            cursor.execute(drop_sql)

        connection.commit()
        print("   ✅ Tabelas antigas removidas")

        # Agora cria as tabelas do zero
        print("   🏗️  Criando tabelas...")
        tabelas_sql = [
            """
            CREATE TABLE fazendas (
                ID_Fazenda INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Fazenda VARCHAR(100) NOT NULL,
                Localizacao_Latitude DECIMAL(10, 8),
                Localizacao_Longitude DECIMAL(11, 8),
                Area_Total_Hectares DECIMAL(10, 2),
                Descricao TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE dispositivos (
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
                FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
                INDEX idx_identificador (Identificador_Unico)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE tipos_sensor (
                ID_Tipo_Sensor INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Tipo VARCHAR(50) NOT NULL UNIQUE,
                Unidade_Medida VARCHAR(20),
                Descricao TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE sensores (
                ID_Sensor INT AUTO_INCREMENT PRIMARY KEY,
                ID_Dispositivo INT NOT NULL,
                ID_Tipo_Sensor INT NOT NULL,
                Status ENUM('Ativo', 'Inativo', 'Manutencao') DEFAULT 'Ativo',
                Ultima_Leitura TIMESTAMP NULL,
                Limite_Minimo_Alerta DECIMAL(10, 4),
                Limite_Maximo_Alerta DECIMAL(10, 4),
                FOREIGN KEY (ID_Dispositivo) REFERENCES dispositivos(ID_Dispositivo) ON DELETE CASCADE,
                FOREIGN KEY (ID_Tipo_Sensor) REFERENCES tipos_sensor(ID_Tipo_Sensor) ON DELETE CASCADE,
                UNIQUE KEY unique_device_sensor (ID_Dispositivo, ID_Tipo_Sensor)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE registro_leituras (
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
            CREATE TABLE usuarios (
                ID_Usuario INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Usuario VARCHAR(50) NOT NULL UNIQUE,
                Senha_Hash VARCHAR(255) NOT NULL,
                Nome_Completo VARCHAR(100),
                Email VARCHAR(100) NOT NULL UNIQUE,
                Status_Conta ENUM('Ativa', 'Inativa', 'Bloqueada') DEFAULT 'Ativa',
                Data_Criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Ultimo_Login TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            # Tabelas extras que podem ser necessárias
            """
            CREATE TABLE niveis_acesso (
                ID_Nivel_Acesso INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Nivel VARCHAR(50) NOT NULL UNIQUE,
                Descricao TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE tipos_atuador (
                ID_Tipo_Atuador INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Tipo VARCHAR(50) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE atuadores (
                ID_Atuador INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Atuador VARCHAR(100) NOT NULL,
                ID_Tipo_Atuador INT,
                ID_Fazenda INT NOT NULL,
                Status_Atual VARCHAR(50),
                Ultimo_Comando_Timestamp TIMESTAMP NULL,
                Parametros_Operacao JSON,
                Endereco_Logico VARCHAR(100),
                Fabricante_Modelo VARCHAR(100),
                FOREIGN KEY (ID_Tipo_Atuador) REFERENCES tipos_atuador(ID_Tipo_Atuador),
                FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE alertas (
                ID_Alerta INT AUTO_INCREMENT PRIMARY KEY,
                ID_Fazenda INT NOT NULL,
                Timestamp_Emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Tipo_Alerta VARCHAR(100),
                Intensidade ENUM('Leve', 'Moderado', 'Severo', 'Critico'),
                Probabilidade DECIMAL(5, 2),
                Mensagem TEXT,
                Status ENUM('Ativo', 'Reconhecido', 'Resolvido') DEFAULT 'Ativo',
                Timestamp_Reconhecimento TIMESTAMP NULL,
                ID_Usuario_Reconheceu INT,
                FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
                FOREIGN KEY (ID_Usuario_Reconheceu) REFERENCES usuarios(ID_Usuario)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE registro_comandos_atuadores (
                ID_Registro_Comando BIGINT AUTO_INCREMENT PRIMARY KEY,
                ID_Atuador INT,
                ID_Usuario_Executor INT,
                Comando_Executado VARCHAR(100),
                Parametros_Comando JSON,
                Timestamp_Comando TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Status_Execucao ENUM('Sucesso', 'Falha', 'Pendente') DEFAULT 'Pendente',
                Mensagem_Retorno TEXT,
                FOREIGN KEY (ID_Atuador) REFERENCES atuadores(ID_Atuador) ON DELETE CASCADE,
                FOREIGN KEY (ID_Usuario_Executor) REFERENCES usuarios(ID_Usuario)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE usuario_fazenda_acesso (
                ID_Usuario INT,
                ID_Fazenda INT,
                ID_Nivel_Acesso INT NOT NULL,
                PRIMARY KEY (ID_Usuario, ID_Fazenda),
                FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
                FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
                FOREIGN KEY (ID_Nivel_Acesso) REFERENCES niveis_acesso(ID_Nivel_Acesso)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            """
            CREATE TABLE documentos_verificados (
                id VARCHAR(36) PRIMARY KEY,
                tabela_origem VARCHAR(100) NOT NULL,
                hash_conteudo VARCHAR(64) NOT NULL UNIQUE,
                data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_usuario_emissor INT,
                FOREIGN KEY (id_usuario_emissor) REFERENCES usuarios(ID_Usuario)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        ]

        for sql in tabelas_sql:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Todas as tabelas recriadas do zero")

        # Dados iniciais
        dados_iniciais = [
            # Níveis de acesso
            """
            INSERT INTO niveis_acesso (Nome_Nivel, Descricao) VALUES
            ('Administrador', 'Acesso completo ao sistema'),
            ('Gerente', 'Gerenciamento de fazenda e usuários'),
            ('Operador', 'Operação e monitoramento'),
            ('Visualizador', 'Apenas visualização de dados')
            """,

            # Fazenda de demonstração
            """
            INSERT INTO fazendas (Nome_Fazenda, Localizacao_Latitude, Localizacao_Longitude, Area_Total_Hectares, Descricao) VALUES
            ('Fazenda Demonstração', -23.5505, -46.6333, 100.50, 'Fazenda para testes e demonstração')
            """,

            # Tipos de sensores
            """
            INSERT INTO tipos_sensor (Nome_Tipo, Unidade_Medida, Descricao) VALUES
            ('temperatura', '°C', 'Sensor de temperatura'),
            ('umidade', '%', 'Sensor de umidade'),
            ('pressao', 'hPa', 'Sensor de pressão'),
            ('campo_eletrico', 'V/m', 'Sensor de campo elétrico'),
            ('precipitacao', 'mm', 'Sensor de precipitação'),
            ('velocidade_vento', 'm/s', 'Sensor de velocidade do vento'),
            ('ph_solo', 'pH', 'Sensor de pH do solo'),
            ('nivel_agua', 'cm', 'Sensor de nível de água')
            """,

            # Tipos de atuadores
            """
            INSERT INTO tipos_atuador (Nome_Tipo) VALUES
            ('Irrigação'),
            ('Ventilação'),
            ('Aquecimento'),
            ('Bomba de Água'),
            ('Sistema de Alerta')
            """,

            # Usuário administrador (senha: admin123)
            """
            INSERT INTO usuarios (Nome_Usuario, Senha_Hash, Nome_Completo, Email) VALUES
            ('admin', 'pbkdf2:sha256:600000$M9xJQQKV$f67de0a7c17bb8bd65b17edc2dd9b47e9e6e1c0ac2ebc95c30b75a5ab0c93b2e', 'Administrador', 'admin@stormguard.com')
            """,

            # Dispositivos de demonstração
            """
            INSERT INTO dispositivos (Identificador_Unico, Nome_Amigavel, Area, ID_Fazenda) VALUES
            ('sensor_area_central_01', 'Estação Meteorológica Central', 'Central', 1),
            ('sensor_area_norte_01', 'Sensor da Estufa Norte', 'Norte', 1),
            ('sensor_area_sul_01', 'Monitor do Campo Sul', 'Sul', 1)
            """
        ]

        for sql in dados_iniciais:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Dados iniciais inseridos")

        # Associa sensores aos dispositivos
        associacoes_sensores = [
            # Dispositivo Central - sensores meteorológicos completos
            """
            INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
            SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
            FROM dispositivos d, tipos_sensor ts
            WHERE d.Identificador_Unico = 'sensor_area_central_01'
            AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'pressao', 'campo_eletrico', 'velocidade_vento')
            """,

            # Dispositivo Norte - sensores de estufa
            """
            INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
            SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
            FROM dispositivos d, tipos_sensor ts
            WHERE d.Identificador_Unico = 'sensor_area_norte_01'
            AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'ph_solo')
            """,

            # Dispositivo Sul - sensores de campo
            """
            INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
            SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
            FROM dispositivos d, tipos_sensor ts
            WHERE d.Identificador_Unico = 'sensor_area_sul_01'
            AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'nivel_agua')
            """
        ]

        for sql in associacoes_sensores:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Sensores associados aos dispositivos")

        # Criar alguns atuadores de exemplo
        atuadores_exemplo = [
            """
            INSERT IGNORE INTO atuadores (Nome_Atuador, ID_Tipo_Atuador, ID_Fazenda, Status_Atual, Endereco_Logico)
            SELECT 'Sistema de Irrigação Central', ta.ID_Tipo_Atuador, f.ID_Fazenda, 'Desligado', 'central_irrig_01'
            FROM tipos_atuador ta, fazendas f
            WHERE ta.Nome_Tipo = 'Irrigação' AND f.Nome_Fazenda = 'Fazenda Demonstração'
            """,

            """
            INSERT IGNORE INTO atuadores (Nome_Atuador, ID_Tipo_Atuador, ID_Fazenda, Status_Atual, Endereco_Logico)
            SELECT 'Bomba de Água do Poço', ta.ID_Tipo_Atuador, f.ID_Fazenda, 'Desligado', 'bomba_poco_01'
            FROM tipos_atuador ta, fazendas f
            WHERE ta.Nome_Tipo = 'Bomba de Água' AND f.Nome_Fazenda = 'Fazenda Demonstração'
            """
        ]

        for sql in atuadores_exemplo:
            cursor.execute(sql)

        connection.commit()
        print("   ✅ Atuadores de exemplo criados")

        cursor.close()
        connection.close()

        return True

    except ImportError:
        print("   ❌ mysql-connector-python não instalado. Execute 'pip install mysql-connector-python'")
        return False
    except Error as e:
        print(f"   ❌ Erro MySQL: {e}")
        print(f"   💡 Verifique se o MySQL está rodando e as credenciais estão corretas")
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

        # Verifica tipos de sensores
        cursor.execute("SELECT COUNT(*) FROM tipos_sensor")
        total_tipos = cursor.fetchone()[0]
        print(f"   🏷️  Tipos de sensores: {total_tipos}")

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

        # Mostra alguns exemplos de associações
        cursor.execute("""
            SELECT d.Nome_Amigavel, ts.Nome_Tipo, s.Status
            FROM dispositivos d
            JOIN sensores s ON d.ID_Dispositivo = s.ID_Dispositivo
            JOIN tipos_sensor ts ON s.ID_Tipo_Sensor = ts.ID_Tipo_Sensor
            ORDER BY d.Nome_Amigavel, ts.Nome_Tipo
        """)

        associacoes = cursor.fetchall()
        if associacoes:
            print("\n   🔗 Exemplos de associações criadas:")
            for disp, tipo, status in associacoes[:10]:  # Mostra até 10 exemplos
                print(f"      • {disp} → {tipo} ({status})")
            if len(associacoes) > 10:
                print(f"      ... e mais {len(associacoes) - 10} associações")

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 StormGuard - Configuração do Banco de Dados")
    print("=" * 60)

    print("ℹ️  Este script irá:")
    print("   • Criar banco de dados MySQL 'stormguard'")
    print("   • ⚠️  REMOVER todas as tabelas existentes")
    print("   • Recriar todas as tabelas do zero")
    print("   • Inserir dados de demonstração")
    print("   • Associar sensores aos dispositivos")
    print("   • Configurar usuário administrador")
    print()
    print("⚠️  ATENÇÃO: Todos os dados existentes serão perdidos!")
    print()

    resposta = input("Continuar? (s/N): ").lower().strip()
    if resposta != 's':
        print("❌ Operação cancelada")
        return False

    print()

    # Configurar banco
    if not executar_script_sql():
        print("❌ Falha na configuração do banco")
        return False

    print()

    # Verificar
    if not verificar_estrutura():
        print("⚠️  Estrutura pode ter problemas")

    print("\n🎉 Banco recriado com sucesso!")
    print("\n📋 Informações importantes:")
    print("   • Banco: stormguard (RECRIADO)")
    print("   • Host: localhost:3306")
    print("   • Usuário MySQL: root (sem senha)")
    print("   • ⚠️  Todos os dados antigos foram removidos")
    print()
    print("🔑 Credenciais da aplicação:")
    print("   • Login: admin")
    print("   • Senha: admin123")
    print()
    print("📡 Dispositivos configurados:")
    print("   • sensor_area_central_01 (5 sensores)")
    print("   • sensor_area_norte_01 (3 sensores)")
    print("   • sensor_area_sul_01 (3 sensores)")

    print("\n🚀 Próximos passos:")
    print("   1. Execute o Flask: flask run")
    print("   2. Acesse: http://localhost:5000")
    print("   3. Faça login com admin/admin123")
    print("   4. Vá em /admin para gerenciar dispositivos")
    print("   5. Teste as associações com: python test_associations.py")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
