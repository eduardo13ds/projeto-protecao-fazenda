-- --------------------------------------------------------------------
-- Schema Otimizado para o Sistema de Alerta de Chuvas (MariaDB)
-- Padrão: Nomes de Tabela em minúsculo, Colunas em CamelCase.
-- --------------------------------------------------------------------

-- Tabela para armazenar os diferentes níveis de permissão dos usuários DENTRO de uma fazenda.
CREATE TABLE `niveis_acesso` (
  `ID_Nivel_Acesso` INT NOT NULL AUTO_INCREMENT,
  `Nome_Nivel` VARCHAR(50) NOT NULL,
  `Descricao` TEXT DEFAULT NULL,
  PRIMARY KEY (`ID_Nivel_Acesso`),
  UNIQUE KEY `uq_niveis_acesso_nome` (`Nome_Nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Define as funções (ex: Gerente, Operador) que um usuário pode ter.';

-- Tabela de usuários do sistema. Não contém mais a permissão direta.
CREATE TABLE `usuarios` (
  `ID_Usuario` INT NOT NULL AUTO_INCREMENT,
  `Nome_Usuario` VARCHAR(50) NOT NULL,
  `Senha_Hash` VARCHAR(255) NOT NULL,
  `Nome_Completo` VARCHAR(100) DEFAULT NULL,
  `Email` VARCHAR(100) NOT NULL,
  `Status_Conta` ENUM('Ativa','Inativa','Bloqueada') DEFAULT 'Ativa',
  `Data_Criacao` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  `Ultimo_Login` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE KEY `uq_usuarios_nome` (`Nome_Usuario`),
  UNIQUE KEY `uq_usuarios_email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Armazena as credenciais e informações básicas dos usuários.';

-- Tabela para cadastrar as fazendas monitoradas. Não contém mais o responsável direto.
CREATE TABLE `fazendas` (
  `ID_Fazenda` INT NOT NULL AUTO_INCREMENT,
  `Nome_Fazenda` VARCHAR(100) NOT NULL,
  `Localizacao_Latitude` DECIMAL(10,8) DEFAULT NULL,
  `Localizacao_Longitude` DECIMAL(11,8) DEFAULT NULL,
  `Area_Total_Hectares` DECIMAL(10,2) DEFAULT NULL,
  `Descricao` TEXT DEFAULT NULL,
  PRIMARY KEY (`ID_Fazenda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Cadastra as propriedades rurais (tenants) do sistema.';

-- Tabela de ligação que define o acesso do usuário a cada fazenda.
CREATE TABLE `usuario_fazenda_acesso` (
  `ID_Usuario` INT NOT NULL,
  `ID_Fazenda` INT NOT NULL,
  `ID_Nivel_Acesso` INT NOT NULL,
  PRIMARY KEY (`ID_Usuario`, `ID_Fazenda`),
  KEY `idx_ufa_usuario` (`ID_Usuario`),
  KEY `idx_ufa_fazenda` (`ID_Fazenda`),
  KEY `idx_ufa_nivel_acesso` (`ID_Nivel_Acesso`),
  CONSTRAINT `fk_ufa_usuarios` FOREIGN KEY (`ID_Usuario`) REFERENCES `usuarios` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `fk_ufa_fazendas` FOREIGN KEY (`ID_Fazenda`) REFERENCES `fazendas` (`ID_Fazenda`) ON DELETE CASCADE,
  CONSTRAINT `fk_ufa_niveis_acesso` FOREIGN KEY (`ID_Nivel_Acesso`) REFERENCES `niveis_acesso` (`ID_Nivel_Acesso`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabela central para a lógica de permissões. Associa usuários a fazendas com um nível de acesso específico.';

-- Tabela de tipos de sensores (ex: Temperatura, Umidade).
CREATE TABLE `tipos_sensor` (
  `ID_Tipo_Sensor` INT NOT NULL AUTO_INCREMENT,
  `Nome_Tipo` VARCHAR(50) NOT NULL,
  `Unidade_Medida` VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (`ID_Tipo_Sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela de tipos de atuadores (ex: Controle de Estufa, Portão).
CREATE TABLE `tipos_atuador` (
  `ID_Tipo_Atuador` INT NOT NULL AUTO_INCREMENT,
  `Nome_Tipo` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`ID_Tipo_Atuador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela para registrar os sensores instalados em cada fazenda.
CREATE TABLE `sensores` (
  `ID_Sensor` INT NOT NULL AUTO_INCREMENT,
  `Nome_Sensor` VARCHAR(100) NOT NULL,
  `ID_Tipo_Sensor` INT DEFAULT NULL,
  `ID_Fazenda` INT NOT NULL,
  `Status` ENUM('Ativo','Inativo','Offline','Manutencao') DEFAULT 'Ativo',
  `Ultima_Leitura` TIMESTAMP NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Limite_Minimo_Alerta` DECIMAL(10,2) DEFAULT NULL,
  `Limite_Maximo_Alerta` DECIMAL(10,2) DEFAULT NULL,
  `Endereco_Logico` VARCHAR(100) DEFAULT NULL,
  `Fabricante_Modelo` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Sensor`),
  KEY `idx_sensores_tipo` (`ID_Tipo_Sensor`),
  KEY `idx_sensores_fazenda` (`ID_Fazenda`),
  CONSTRAINT `fk_sensores_tipos_sensor` FOREIGN KEY (`ID_Tipo_Sensor`) REFERENCES `tipos_sensor` (`ID_Tipo_Sensor`) ON DELETE SET NULL,
  CONSTRAINT `fk_sensores_fazendas` FOREIGN KEY (`ID_Fazenda`) REFERENCES `fazendas` (`ID_Fazenda`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela para registrar os atuadores instalados em cada fazenda.
CREATE TABLE `atuadores` (
  `ID_Atuador` INT NOT NULL AUTO_INCREMENT,
  `Nome_Atuador` VARCHAR(100) NOT NULL,
  `ID_Tipo_Atuador` INT DEFAULT NULL,
  `ID_Fazenda` INT NOT NULL,
  `Status_Atual` VARCHAR(50) DEFAULT NULL,
  `Ultimo_Comando_Timestamp` TIMESTAMP NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Parametros_Operacao` JSON DEFAULT NULL,
  `Endereco_Logico` VARCHAR(100) DEFAULT NULL,
  `Fabricante_Modelo` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Atuador`),
  KEY `idx_atuadores_tipo` (`ID_Tipo_Atuador`),
  KEY `idx_atuadores_fazenda` (`ID_Fazenda`),
  CONSTRAINT `fk_atuadores_tipos_atuador` FOREIGN KEY (`ID_Tipo_Atuador`) REFERENCES `tipos_atuador` (`ID_Tipo_Atuador`) ON DELETE SET NULL,
  CONSTRAINT `fk_atuadores_fazendas` FOREIGN KEY (`ID_Fazenda`) REFERENCES `fazendas` (`ID_Fazenda`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela de log para todas as leituras recebidas dos sensores.
CREATE TABLE `registro_leituras` (
  `ID_Leitura` BIGINT NOT NULL AUTO_INCREMENT,
  `ID_Sensor` INT NOT NULL,
  `Valor_Leitura` VARCHAR(255) NOT NULL,
  `Timestamp_Leitura` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  `Qualidade` ENUM('Confiavel','Ruido','Fora da Faixa') DEFAULT 'Confiavel',
  PRIMARY KEY (`ID_Leitura`),
  KEY `idx_leituras_sensor_timestamp` (`ID_Sensor`, `Timestamp_Leitura`),
  CONSTRAINT `fk_leituras_sensores` FOREIGN KEY (`ID_Sensor`) REFERENCES `sensores` (`ID_Sensor`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela para registrar os alertas gerados pelo sistema.
CREATE TABLE `alertas` (
  `ID_Alerta` INT NOT NULL AUTO_INCREMENT,
  `ID_Fazenda` INT NOT NULL,
  `Timestamp_Emissao` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  `Tipo_Alerta` VARCHAR(100) DEFAULT NULL,
  `Intensidade` ENUM('Leve','Moderado','Severo','Critico') DEFAULT NULL,
  `Probabilidade` DECIMAL(5,2) DEFAULT NULL,
  `Mensagem` TEXT DEFAULT NULL,
  `Status` ENUM('Ativo','Reconhecido','Resolvido') DEFAULT 'Ativo',
  `Timestamp_Reconhecimento` TIMESTAMP NULL DEFAULT NULL,
  `ID_Usuario_Reconheceu` INT DEFAULT NULL,
  PRIMARY KEY (`ID_Alerta`),
  KEY `idx_alertas_fazenda` (`ID_Fazenda`),
  KEY `idx_alertas_usuario` (`ID_Usuario_Reconheceu`),
  CONSTRAINT `fk_alertas_fazendas` FOREIGN KEY (`ID_Fazenda`) REFERENCES `fazendas` (`ID_Fazenda`) ON DELETE CASCADE,
  CONSTRAINT `fk_alertas_usuarios` FOREIGN KEY (`ID_Usuario_Reconheceu`) REFERENCES `usuarios` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabela de log para todos os comandos enviados aos atuadores.
CREATE TABLE `registro_comandos_atuadores` (
  `ID_Registro_Comando` BIGINT NOT NULL AUTO_INCREMENT,
  `ID_Atuador` INT DEFAULT NULL,
  `ID_Usuario_Executor` INT DEFAULT NULL,
  `Comando_Executado` VARCHAR(100) DEFAULT NULL,
  `Parametros_Comando` JSON DEFAULT NULL,
  `Timestamp_Comando` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  `Status_Execucao` ENUM('Sucesso','Falha','Pendente') DEFAULT 'Pendente',
  `Mensagem_Retorno` TEXT DEFAULT NULL,
  PRIMARY KEY (`ID_Registro_Comando`),
  KEY `idx_comandos_atuador` (`ID_Atuador`),
  KEY `idx_comandos_usuario` (`ID_Usuario_Executor`),
  CONSTRAINT `fk_comandos_atuadores` FOREIGN KEY (`ID_Atuador`) REFERENCES `atuadores` (`ID_Atuador`) ON DELETE SET NULL,
  CONSTRAINT `fk_comandos_usuarios` FOREIGN KEY (`ID_Usuario_Executor`) REFERENCES `usuarios` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
