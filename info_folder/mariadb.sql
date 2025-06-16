-- -------------------------------------------------------------
-- -------------------------------------------------------------
-- TablePlus 1.2.6
--
-- https://tableplus.com/
--
-- Database: mariadb
-- Generation Time: 2025-06-14 16:44:18.424878
-- -------------------------------------------------------------

CREATE TABLE `Alertas` (
  `ID_Alerta` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Fazenda` int(11) DEFAULT NULL,
  `Timestamp_Emissao` timestamp NOT NULL DEFAULT current_timestamp(),
  `Tipo_Alerta` varchar(100) DEFAULT NULL,
  `Intensidade` enum('Leve','Moderado','Severo','Critico') DEFAULT NULL,
  `Probabilidade` decimal(5,2) DEFAULT NULL,
  `Mensagem` text DEFAULT NULL,
  `Status` enum('Ativo','Reconhecido','Resolvido') DEFAULT 'Ativo',
  `Timestamp_Reconhecimento` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `ID_Usuario_Reconheceu` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID_Alerta`),
  KEY `ID_Fazenda` (`ID_Fazenda`),
  KEY `ID_Usuario_Reconheceu` (`ID_Usuario_Reconheceu`),
  CONSTRAINT `Alertas_ibfk_1` FOREIGN KEY (`ID_Fazenda`) REFERENCES `Fazendas` (`ID_Fazenda`) ON DELETE CASCADE,
  CONSTRAINT `Alertas_ibfk_2` FOREIGN KEY (`ID_Usuario_Reconheceu`) REFERENCES `Usuarios` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Atuadores` (
  `ID_Atuador` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Atuador` varchar(100) NOT NULL,
  `ID_Tipo_Atuador` int(11) DEFAULT NULL,
  `ID_Fazenda` int(11) DEFAULT NULL,
  `Status_Atual` varchar(50) DEFAULT NULL,
  `Ultimo_Comando_Timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Parametros_Operacao` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`Parametros_Operacao`)),
  `Endereco_Logico` varchar(100) DEFAULT NULL,
  `Fabricante_Modelo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Atuador`),
  KEY `ID_Tipo_Atuador` (`ID_Tipo_Atuador`),
  KEY `ID_Fazenda` (`ID_Fazenda`),
  CONSTRAINT `Atuadores_ibfk_1` FOREIGN KEY (`ID_Tipo_Atuador`) REFERENCES `Tipos_Atuador` (`ID_Tipo_Atuador`) ON DELETE SET NULL,
  CONSTRAINT `Atuadores_ibfk_2` FOREIGN KEY (`ID_Fazenda`) REFERENCES `Fazendas` (`ID_Fazenda`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Fazendas` (
  `ID_Fazenda` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Fazenda` varchar(100) NOT NULL,
  `Localizacao_Latitude` decimal(10,8) DEFAULT NULL,
  `Localizacao_Longitude` decimal(11,8) DEFAULT NULL,
  `Area_Total_Hectares` decimal(10,2) DEFAULT NULL,
  `ID_Usuario_Responsavel` int(11) DEFAULT NULL,
  `Descricao` text DEFAULT NULL,
  PRIMARY KEY (`ID_Fazenda`),
  KEY `ID_Usuario_Responsavel` (`ID_Usuario_Responsavel`),
  CONSTRAINT `Fazendas_ibfk_1` FOREIGN KEY (`ID_Usuario_Responsavel`) REFERENCES `Usuarios` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Niveis_Acesso` (
  `ID_Nivel_Acesso` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Nivel` varchar(50) NOT NULL,
  `Descricao` text DEFAULT NULL,
  PRIMARY KEY (`ID_Nivel_Acesso`),
  UNIQUE KEY `Nome_Nivel` (`Nome_Nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Registro_Comandos_Atuadores` (
  `ID_Registro_Comando` bigint(20) NOT NULL AUTO_INCREMENT,
  `ID_Atuador` int(11) DEFAULT NULL,
  `ID_Usuario_Executor` int(11) DEFAULT NULL,
  `Comando_Executado` varchar(100) DEFAULT NULL,
  `Parametros_Comando` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`Parametros_Comando`)),
  `Timestamp_Comando` timestamp NOT NULL DEFAULT current_timestamp(),
  `Status_Execucao` enum('Sucesso','Falha','Pendente') DEFAULT 'Pendente',
  `Mensagem_Retorno` text DEFAULT NULL,
  PRIMARY KEY (`ID_Registro_Comando`),
  KEY `ID_Atuador` (`ID_Atuador`),
  KEY `ID_Usuario_Executor` (`ID_Usuario_Executor`),
  CONSTRAINT `Registro_Comandos_Atuadores_ibfk_1` FOREIGN KEY (`ID_Atuador`) REFERENCES `Atuadores` (`ID_Atuador`) ON DELETE SET NULL,
  CONSTRAINT `Registro_Comandos_Atuadores_ibfk_2` FOREIGN KEY (`ID_Usuario_Executor`) REFERENCES `Usuarios` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Registro_Leituras` (
  `ID_Leitura` bigint(20) NOT NULL AUTO_INCREMENT,
  `ID_Sensor` int(11) DEFAULT NULL,
  `Valor_Leitura` varchar(255) NOT NULL,
  `Timestamp_Leitura` timestamp NOT NULL DEFAULT current_timestamp(),
  `Qualidade` enum('Confiavel','Ruido','Fora da Faixa') DEFAULT 'Confiavel',
  PRIMARY KEY (`ID_Leitura`),
  KEY `ID_Sensor` (`ID_Sensor`),
  CONSTRAINT `Registro_Leituras_ibfk_1` FOREIGN KEY (`ID_Sensor`) REFERENCES `Sensores` (`ID_Sensor`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Sensores` (
  `ID_Sensor` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Sensor` varchar(100) NOT NULL,
  `ID_Tipo_Sensor` int(11) DEFAULT NULL,
  `ID_Fazenda` int(11) DEFAULT NULL,
  `Status` enum('Ativo','Inativo','Offline','Manutencao') DEFAULT 'Ativo',
  `Ultima_Leitura` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Limite_Minimo_Alerta` decimal(10,2) DEFAULT NULL,
  `Limite_Maximo_Alerta` decimal(10,2) DEFAULT NULL,
  `Endereco_Logico` varchar(100) DEFAULT NULL,
  `Fabricante_Modelo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Sensor`),
  KEY `ID_Tipo_Sensor` (`ID_Tipo_Sensor`),
  KEY `ID_Fazenda` (`ID_Fazenda`),
  CONSTRAINT `Sensores_ibfk_1` FOREIGN KEY (`ID_Tipo_Sensor`) REFERENCES `Tipos_Sensor` (`ID_Tipo_Sensor`) ON DELETE SET NULL,
  CONSTRAINT `Sensores_ibfk_2` FOREIGN KEY (`ID_Fazenda`) REFERENCES `Fazendas` (`ID_Fazenda`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Tipos_Atuador` (
  `ID_Tipo_Atuador` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`ID_Tipo_Atuador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Tipos_Sensor` (
  `ID_Tipo_Sensor` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Tipo` varchar(50) NOT NULL,
  `Unidade_Medida` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_Tipo_Sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Usuarios` (
  `ID_Usuario` int(11) NOT NULL AUTO_INCREMENT,
  `Nome_Usuario` varchar(50) NOT NULL,
  `Senha_Hash` varchar(255) NOT NULL,
  `Nome_Completo` varchar(100) DEFAULT NULL,
  `Email` varchar(100) NOT NULL,
  `ID_Nivel_Acesso` int(11) DEFAULT NULL,
  `Status_Conta` enum('Ativa','Inativa','Bloqueada') DEFAULT 'Ativa',
  `Data_Criacao` timestamp NOT NULL DEFAULT current_timestamp(),
  `Ultimo_Login` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE KEY `Nome_Usuario` (`Nome_Usuario`),
  UNIQUE KEY `Email` (`Email`),
  KEY `ID_Nivel_Acesso` (`ID_Nivel_Acesso`),
  CONSTRAINT `Usuarios_ibfk_1` FOREIGN KEY (`ID_Nivel_Acesso`) REFERENCES `Niveis_Acesso` (`ID_Nivel_Acesso`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

