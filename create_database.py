#!/usr/bin/env python3
"""
Script para criar e configurar o banco de dados MySQL do StormGuard do zero.
Execute este script para criar todas as tabelas necessárias.

Uso:
    python create_database.py
"""

import sys
import os
import mysql.connector
from mysql.connector import Error

# Configurações do banco
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'stormguard'

def conectar_mysql():
    """Conecta ao MySQL sem especificar um banco."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

def conectar_banco():
    """Conecta ao banco stormguard."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"❌ Erro ao conectar ao banco {DB_NAME}: {e}")
        return None

def criar_banco():
    """Cria o banco de dados se não existir."""
    print("🗄️  Criando banco de dados...")

    connection = conectar_mysql()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_NAME}")
        print(f"   ✅ Banco '{DB_NAME}' criado/verificado com sucesso")
        return True
    except Error as e:
        print(f"   ❌ Erro ao criar banco: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def executar_sql(sql_commands):
    """Executa uma lista de comandos SQL."""
    connection = conectar_banco()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        for sql in sql_commands:
            if sql.strip():
                cursor.execute(sql)

        connection.commit()
        return True
    except Error as e:
        print(f"   ❌ Erro ao executar SQL: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def criar_tabelas():
    """Cria todas as tabelas necessárias."""
    print("📋 Criando tabelas...")

    # SQL para criar todas as tabelas
    sql_commands = [
        # 1. Tabela de níveis de acesso
        """
        CREATE TABLE IF NOT EXISTS niveis_acesso (
            ID_Nivel_Acesso INT AUTO_INCREMENT PRIMARY KEY,
            Nome_Nivel VARCHAR(50) NOT NULL UNIQUE,
            Descricao TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 2. Tabela de usuários
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
        """,

        # 3. Tabela de fazendas
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

        # 4. Tabela de associação usuário-fazenda-acesso
        """
        CREATE TABLE IF NOT EXISTS usuario_fazenda_acesso (
            ID_Usuario INT,
            ID_Fazenda INT,
            ID_Nivel_Acesso INT NOT NULL,
            PRIMARY KEY (ID_Usuario, ID_Fazenda),
            FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
            FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
            FOREIGN KEY (ID_Nivel_Acesso) REFERENCES niveis_acesso(ID_Nivel_Acesso)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 5. Tabela de dispositivos
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
            FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
            INDEX idx_identificador (Identificador_Unico),
            INDEX idx_fazenda (ID_Fazenda),
            INDEX idx_status (Status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 6. Tabela de tipos de sensores
        """
        CREATE TABLE IF NOT EXISTS tipos_sensor (
            ID_Tipo_Sensor INT AUTO_INCREMENT PRIMARY KEY,
            Nome_Tipo VARCHAR(50) NOT NULL UNIQUE,
            Unidade_Medida VARCHAR(20),
            Descricao TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 7. Tabela de sensores
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
            FOREIGN KEY (ID_Tipo_Sensor) REFERENCES tipos_sensor(ID_Tipo_Sensor) ON DELETE CASCADE,
            UNIQUE KEY unique_device_sensor (ID_Dispositivo, ID_Tipo_Sensor),
            INDEX idx_dispositivo (ID_Dispositivo),
            INDEX idx_tipo_sensor (ID_Tipo_Sensor),
            INDEX idx_status (Status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 8. Tabela de registros de leitura
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
            INDEX idx_sensor_timestamp (ID_Sensor, Timestamp_Leitura),
            INDEX idx_timestamp (Timestamp_Leitura),
            INDEX idx_qualidade (Qualidade)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 9. Tabela de tipos de atuadores
        """
        CREATE TABLE IF NOT EXISTS tipos_atuador (
            ID_Tipo_Atuador INT AUTO_INCREMENT PRIMARY KEY,
            Nome_Tipo VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 10. Tabela de atuadores
        """
        CREATE TABLE IF NOT EXISTS atuadores (
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
            FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
            INDEX idx_fazenda (ID_Fazenda),
            INDEX idx_tipo (ID_Tipo_Atuador)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 11. Tabela de alertas
        """
        CREATE TABLE IF NOT EXISTS alertas (
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
            FOREIGN KEY (ID_Usuario_Reconheceu) REFERENCES usuarios(ID_Usuario),
            INDEX idx_fazenda_status (ID_Fazenda, Status),
            INDEX idx_timestamp (Timestamp_Emissao)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 12. Tabela de registro de comandos de atuadores
        """
        CREATE TABLE IF NOT EXISTS registro_comandos_atuadores (
            ID_Registro_Comando BIGINT AUTO_INCREMENT PRIMARY KEY,
            ID_Atuador INT,
            ID_Usuario_Executor INT,
            Comando_Executado VARCHAR(100),
            Parametros_Comando JSON,
            Timestamp_Comando TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Status_Execucao ENUM('Sucesso', 'Falha', 'Pendente') DEFAULT 'Pendente',
            Mensagem_Retorno TEXT,
            FOREIGN KEY (ID_Atuador) REFERENCES atuadores(ID_Atuador) ON DELETE CASCADE,
            FOREIGN KEY (ID_Usuario_Executor) REFERENCES usuarios(ID_Usuario),
            INDEX idx_atuador_timestamp (ID_Atuador, Timestamp_Comando),
            INDEX idx_usuario (ID_Usuario_Executor)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,

        # 13. Tabela de documentos de verificação
        """
        CREATE TABLE IF NOT EXISTS documentos_verificados (
            id VARCHAR(36) PRIMARY KEY,
            tabela_origem VARCHAR(100) NOT NULL,
            hash_conteudo VARCHAR(64) NOT NULL UNIQUE,
            data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            id_usuario_emissor INT,
            FOREIGN KEY (id_usuario_emissor) REFERENCES usuarios(ID_Usuario),
            INDEX idx_hash (hash_conteudo),
            INDEX idx_data (data_emissao)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    ]

    if executar_sql(sql_commands):
        print("   ✅ Todas as tabelas criadas com sucesso")
        return True
    else:
        return False

def verificar_tabelas():
    """Verifica se todas as tabelas foram criadas corretamente."""
    print("🔍 Verificando tabelas criadas...")

    connection = conectar_banco()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = [table[0] for table in cursor.fetchall()]

        tabelas_esperadas = [
            'alertas', 'atuadores', 'dispositivos', 'documentos_verificados',
            'fazendas', 'niveis_acesso', 'registro_comandos_atuadores',
            'registro_leituras', 'sensores', 'tipos_atuador', 'tipos_sensor',
            'usuario_fazenda_acesso', 'usuarios'
        ]

        print(f"   📊 Tabelas encontradas: {len(tabelas)}")

        for tabela in tabelas_esperadas:
            if tabela in tabelas:
                print(f"   ✅ {tabela}")
            else:
                print(f"   ❌ {tabela} - FALTANDO")

        # Verifica estrutura da tabela dispositivos especificamente
        cursor.execute("DESCRIBE dispositivos")
        colunas_dispositivos = [col[0] for col in cursor.fetchall()]
        print(f"\n   🔍 Colunas da tabela dispositivos: {', '.join(colunas_dispositivos)}")

        # Verifica estrutura da tabela sensores
        cursor.execute("DESCRIBE sensores")
        colunas_sensores = [col[0] for col in cursor.fetchall()]
        print(f"   🔍 Colunas da tabela sensores: {', '.join(colunas_sensores)}")

        return len([t for t in tabelas_esperadas if t in tabelas]) == len(tabelas_esperadas)

    except Error as e:
        print(f"   ❌ Erro ao verificar tabelas: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def inserir_dados_basicos():
    """Insere dados básicos necessários para o funcionamento."""
    print("🌱 Inserindo dados básicos...")

    sql_commands = [
        # Níveis de acesso
        """
        INSERT IGNORE INTO niveis_acesso (Nome_Nivel, Descricao) VALUES
        ('Administrador', 'Acesso completo ao sistema'),
        ('Gerente', 'Gerenciamento de fazenda e usuários'),
        ('Operador', 'Operação e monitoramento'),
        ('Visualizador', 'Apenas visualização de dados')
        """,

        # Usuário administrador
        """
        INSERT IGNORE INTO usuarios (Nome_Usuario, Senha_Hash, Nome_Completo, Email, Status_Conta) VALUES
        ('admin', 'pbkdf2:sha256:600000$M9xJQQKV$f67de0a7c17bb8bd65b17edc2dd9b47e9e6e1c0ac2ebc95c30b75a5ab0c93b2e', 'Administrador do Sistema', 'admin@stormguard.com.br', 'Ativa')
        """,

        # Fazenda de demonstração
        """
        INSERT IGNORE INTO fazendas (Nome_Fazenda, Localizacao_Latitude, Localizacao_Longitude, Area_Total_Hectares, Descricao) VALUES
        ('Fazenda Demonstração', -23.5505, -46.6333, 100.50, 'Fazenda para testes e demonstração do sistema StormGuard')
        """,

        # Tipos de sensores
        """
        INSERT IGNORE INTO tipos_sensor (Nome_Tipo, Unidade_Medida, Descricao) VALUES
        ('temperatura', '°C', 'Sensor de temperatura ambiente'),
        ('umidade', '%', 'Sensor de umidade relativa do ar'),
        ('pressao', 'hPa', 'Sensor de pressão atmosférica'),
        ('precipitacao', 'mm', 'Sensor de precipitação (chuva)'),
        ('velocidade_vento', 'm/s', 'Sensor de velocidade do vento'),
        ('direcao_vento', '°', 'Sensor de direção do vento'),
        ('radiacao_solar', 'W/m²', 'Sensor de radiação solar'),
        ('ph_solo', 'pH', 'Sensor de pH do solo'),
        ('campo_eletrico', 'V/m', 'Sensor de campo elétrico atmosférico'),
        ('nivel_agua', 'cm', 'Sensor de nível de água')
        """,

        # Tipos de atuadores
        """
        INSERT IGNORE INTO tipos_atuador (Nome_Tipo) VALUES
        ('Irrigação'),
        ('Ventilação'),
        ('Aquecimento'),
        ('Iluminação'),
        ('Bomba de Água'),
        ('Válvula Solenoide'),
        ('Sistema de Alerta')
        """
    ]

    if executar_sql(sql_commands):
        print("   ✅ Dados básicos inseridos com sucesso")
        return True
    else:
        return False

def main():
    """Função principal."""
    print("🚀 StormGuard - Configuração do Banco de Dados")
    print("=" * 60)

    # Testa conexão com MySQL
    print("🔌 Testando conexão com MySQL...")
    connection = conectar_mysql()
    if not connection:
        print("❌ Não foi possível conectar ao MySQL. Verifique se:")
        print("   • MySQL está rodando")
        print("   • Credenciais estão corretas")
        print(f"   • Host: {DB_HOST}:{DB_PORT}")
        print(f"   • Usuário: {DB_USER}")
        return False
    else:
        print("   ✅ Conexão com MySQL estabelecida")
        connection.close()

    # Cria o banco de dados
    if not criar_banco():
        return False

    # Cria as tabelas
    if not criar_tabelas():
        return False

    # Verifica as tabelas
    if not verificar_tabelas():
        print("⚠️  Algumas tabelas podem não ter sido criadas corretamente")

    # Insere dados básicos
    if not inserir_dados_basicos():
        return False

    print("\n🎉 Banco de dados configurado com sucesso!")
    print("\n📋 Próximos passos:")
    print("   1. Execute: python setup_database.py")
    print("   2. Execute: python test_associations.py")
    print("   3. Inicie a aplicação Flask")
    print("\n🔑 Credenciais de acesso:")
    print("   Login: admin")
    print("   Senha: admin123")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
