-- StormGuard Database Creation Script
-- Execute este script no MySQL para criar todas as tabelas necessárias

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS stormguard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stormguard;

-- 1. Tabela de fazendas (deve ser criada primeiro por causa das foreign keys)
CREATE TABLE IF NOT EXISTS fazendas (
    ID_Fazenda INT AUTO_INCREMENT PRIMARY KEY,
    Nome_Fazenda VARCHAR(100) NOT NULL,
    Localizacao_Latitude DECIMAL(10, 8),
    Localizacao_Longitude DECIMAL(11, 8),
    Area_Total_Hectares DECIMAL(10, 2),
    Descricao TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Tabela de dispositivos
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tabela de tipos de sensores
CREATE TABLE IF NOT EXISTS tipos_sensor (
    ID_Tipo_Sensor INT AUTO_INCREMENT PRIMARY KEY,
    Nome_Tipo VARCHAR(50) NOT NULL UNIQUE,
    Unidade_Medida VARCHAR(20),
    Descricao TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Tabela de sensores
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Tabela de registros de leitura
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    ID_Usuario INT AUTO_INCREMENT PRIMARY KEY,
    Nome_Usuario VARCHAR(50) NOT NULL UNIQUE,
    Senha_Hash VARCHAR(255) NOT NULL,
    Nome_Completo VARCHAR(100),
    Email VARCHAR(100) NOT NULL UNIQUE,
    Status_Conta ENUM('Ativa', 'Inativa', 'Bloqueada') DEFAULT 'Ativa',
    Data_Criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Ultimo_Login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Tabela de níveis de acesso
CREATE TABLE IF NOT EXISTS niveis_acesso (
    ID_Nivel_Acesso INT AUTO_INCREMENT PRIMARY KEY,
    Nome_Nivel VARCHAR(50) NOT NULL UNIQUE,
    Descricao TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Tabela de associação usuário-fazenda-acesso
CREATE TABLE IF NOT EXISTS usuario_fazenda_acesso (
    ID_Usuario INT,
    ID_Fazenda INT,
    ID_Nivel_Acesso INT NOT NULL,
    PRIMARY KEY (ID_Usuario, ID_Fazenda),
    FOREIGN KEY (ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
    FOREIGN KEY (ID_Fazenda) REFERENCES fazendas(ID_Fazenda) ON DELETE CASCADE,
    FOREIGN KEY (ID_Nivel_Acesso) REFERENCES niveis_acesso(ID_Nivel_Acesso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Tabela de tipos de atuadores
CREATE TABLE IF NOT EXISTS tipos_atuador (
    ID_Tipo_Atuador INT AUTO_INCREMENT PRIMARY KEY,
    Nome_Tipo VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Tabela de atuadores
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Tabela de alertas
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Tabela de registro de comandos de atuadores
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Tabela de documentos de verificação
CREATE TABLE IF NOT EXISTS documentos_verificados (
    id VARCHAR(36) PRIMARY KEY,
    tabela_origem VARCHAR(100) NOT NULL,
    hash_conteudo VARCHAR(64) NOT NULL UNIQUE,
    data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario_emissor INT,
    FOREIGN KEY (id_usuario_emissor) REFERENCES usuarios(ID_Usuario),
    INDEX idx_hash (hash_conteudo),
    INDEX idx_data (data_emissao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Inserir dados básicos necessários
INSERT IGNORE INTO niveis_acesso (Nome_Nivel, Descricao) VALUES
('Administrador', 'Acesso completo ao sistema'),
('Gerente', 'Gerenciamento de fazenda e usuários'),
('Operador', 'Operação e monitoramento'),
('Visualizador', 'Apenas visualização de dados');

-- Usuário administrador (senha: admin123)
INSERT IGNORE INTO usuarios (Nome_Usuario, Senha_Hash, Nome_Completo, Email, Status_Conta) VALUES
('admin', 'pbkdf2:sha256:600000$M9xJQQKV$f67de0a7c17bb8bd65b17edc2dd9b47e9e6e1c0ac2ebc95c30b75a5ab0c93b2e', 'Administrador do Sistema', 'admin@stormguard.com.br', 'Ativa');

-- Fazenda de demonstração
INSERT IGNORE INTO fazendas (Nome_Fazenda, Localizacao_Latitude, Localizacao_Longitude, Area_Total_Hectares, Descricao) VALUES
('Fazenda Demonstração', -23.5505, -46.6333, 100.50, 'Fazenda para testes e demonstração do sistema StormGuard');

-- Tipos de sensores
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
('nivel_agua', 'cm', 'Sensor de nível de água');

-- Tipos de atuadores
INSERT IGNORE INTO tipos_atuador (Nome_Tipo) VALUES
('Irrigação'),
('Ventilação'),
('Aquecimento'),
('Iluminação'),
('Bomba de Água'),
('Válvula Solenoide'),
('Sistema de Alerta');

-- Dispositivos de demonstração
INSERT IGNORE INTO dispositivos (Identificador_Unico, Nome_Amigavel, Area, ID_Fazenda, Status) VALUES
('sensor_area_central_01', 'Estação Meteorológica Central', 'Central', 1, 'Ativo'),
('sensor_area_norte_01', 'Sensor da Estufa Norte', 'Norte', 1, 'Ativo'),
('sensor_area_sul_01', 'Monitor do Campo Sul', 'Sul', 1, 'Ativo');

-- Associar sensores aos dispositivos (usando subqueries para garantir que os IDs existam)
INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
FROM dispositivos d, tipos_sensor ts
WHERE d.Identificador_Unico = 'sensor_area_central_01'
AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'pressao', 'campo_eletrico', 'velocidade_vento');

INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
FROM dispositivos d, tipos_sensor ts
WHERE d.Identificador_Unico = 'sensor_area_norte_01'
AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'ph_solo');

INSERT IGNORE INTO sensores (ID_Dispositivo, ID_Tipo_Sensor, Status)
SELECT d.ID_Dispositivo, ts.ID_Tipo_Sensor, 'Ativo'
FROM dispositivos d, tipos_sensor ts
WHERE d.Identificador_Unico = 'sensor_area_sul_01'
AND ts.Nome_Tipo IN ('temperatura', 'umidade', 'nivel_agua');

-- Atuadores de exemplo
INSERT IGNORE INTO atuadores (Nome_Atuador, ID_Tipo_Atuador, ID_Fazenda, Status_Atual, Endereco_Logico)
SELECT 'Sistema de Irrigação Central', ta.ID_Tipo_Atuador, f.ID_Fazenda, 'Desligado', 'central_irrig_01'
FROM tipos_atuador ta, fazendas f
WHERE ta.Nome_Tipo = 'Irrigação' AND f.Nome_Fazenda = 'Fazenda Demonstração';

INSERT IGNORE INTO atuadores (Nome_Atuador, ID_Tipo_Atuador, ID_Fazenda, Status_Atual, Endereco_Logico)
SELECT 'Bomba de Água do Poço', ta.ID_Tipo_Atuador, f.ID_Fazenda, 'Desligado', 'bomba_poco_01'
FROM tipos_atuador ta, fazendas f
WHERE ta.Nome_Tipo = 'Bomba de Água' AND f.Nome_Fazenda = 'Fazenda Demonstração';

-- Verificação final
SELECT 'Tabelas criadas com sucesso!' as Status;
SELECT COUNT(*) as Total_Dispositivos FROM dispositivos;
SELECT COUNT(*) as Total_Sensores FROM sensores;
SELECT COUNT(*) as Total_Tipos_Sensor FROM tipos_sensor;
SELECT 'Configuração concluída!' as Resultado;
