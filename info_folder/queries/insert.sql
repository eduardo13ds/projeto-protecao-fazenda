-- --------------------------------------------------------------------
-- Script de Inserção de Dados Exemplares
-- Versão com Controle de Acesso por Fazenda (Multi-Tenancy)
-- --------------------------------------------------------------------
-- A ordem de inserção respeita as chaves estrangeiras.

-- 1. Níveis de Acesso
-- Define as funções que um usuário pode ter dentro de uma fazenda.
INSERT INTO `niveis_acesso` (`ID_Nivel_Acesso`, `Nome_Nivel`, `Descricao`) VALUES
(1, 'Gerente', 'Acesso completo aos dados e atuadores de uma fazenda designada.'),
(2, 'Operador', 'Pode visualizar dados, receber alertas e operar atuadores.'),
(3, 'Visualizador', 'Acesso somente leitura aos dados da fazenda.');

-- 2. Usuários
-- Cadastra os usuários do sistema. As permissões são definidas depois.
INSERT INTO `usuarios` (`ID_Usuario`, `Nome_Usuario`, `Senha_Hash`, `Nome_Completo`, `Email`, `Status_Conta`, `Data_Criacao`, `Ultimo_Login`) VALUES
(1, 'joao.silva', 'hash_segura_joao', 'João Silva', 'joao.silva@email.com', 'Ativa', '2025-01-10 08:00:00', '2025-06-14 17:00:00'),
(2, 'maria.oliveira', 'hash_segura_maria', 'Maria Oliveira', 'maria.oliveira@email.com', 'Ativa', '2025-02-15 10:20:00', '2025-06-14 17:25:00'),
(3, 'carlos.p', 'hash_segura_carlos', 'Carlos Pereira', 'carlos.pereira@email.com', 'Ativa', '2025-03-20 11:00:00', '2025-06-14 17:10:00');

-- 3. Fazendas
-- Cadastra as propriedades rurais (tenants) do sistema.
INSERT INTO `fazendas` (`ID_Fazenda`, `Nome_Fazenda`, `Localizacao_Latitude`, `Localizacao_Longitude`, `Area_Total_Hectares`, `Descricao`) VALUES
(1, 'Fazenda Sol Nascente', -25.4284, -49.2733, 500.50, 'Grande fazenda produtora de grãos e com gado leiteiro.'),
(2, 'Sítio Bela Vista', -23.5505, -46.6333, 50.75, 'Pequeno sítio com foco em horticultura e estufas.');

-- 4. Associação de Acesso (Usuário <-> Fazenda)
-- Esta é a etapa crucial que define QUEM pode acessar O QUÊ.
INSERT INTO `usuario_fazenda_acesso` (`ID_Usuario`, `ID_Fazenda`, `ID_Nivel_Acesso`) VALUES
-- Maria Oliveira é Gerente (1) da Fazenda Sol Nascente (1)
(2, 1, 1),
-- Carlos Pereira é Operador (2) da Fazenda Sol Nascente (1)
(3, 1, 2),
-- João Silva é Gerente (1) do Sítio Bela Vista (2)
(1, 2, 1);

-- 5. Tipos de Dispositivos
INSERT INTO `tipos_sensor` (`ID_Tipo_Sensor`, `Nome_Tipo`, `Unidade_Medida`) VALUES
(1, 'Temperatura', '°C'), (2, 'Umidade Relativa', '%'), (3, 'Pressão Barométrica', 'hPa');
INSERT INTO `tipos_atuador` (`ID_Tipo_Atuador`, `Nome_Tipo`) VALUES
(1, 'Controle de Estufa'), (2, 'Controle de Portão');

-- 6. Sensores e Atuadores (associados a uma fazenda específica)
-- Dispositivos da Fazenda Sol Nascente (ID_Fazenda = 1)
INSERT INTO `sensores` (`Nome_Sensor`, `ID_Tipo_Sensor`, `ID_Fazenda`, `Endereco_Logico`) VALUES
('DHT22 - Umidade Setor Norte', 2, 1, 'esp32/dht22/umid/norte'),
('BMP280 - Pressão Central', 3, 1, 'esp32/bmp280/pressao');
INSERT INTO `atuadores` (`Nome_Atuador`, `ID_Tipo_Atuador`, `ID_Fazenda`, `Status_Atual`, `Endereco_Logico`) VALUES
('Ventilação Estufa Horta', 1, 1, 'Aberto', 'esp32/rele/estufa1'),
('Portão Celeiro Principal', 2, 1, 'Aberto', 'esp32/rele/celeiro_principal');

-- Dispositivos do Sítio Bela Vista (ID_Fazenda = 2)
INSERT INTO `sensores` (`Nome_Sensor`, `ID_Tipo_Sensor`, `ID_Fazenda`, `Endereco_Logico`) VALUES
('Sensor de Umidade do Solo A', 2, 2, 'esp32/solo/a');
INSERT INTO `atuadores` (`Nome_Atuador`, `ID_Tipo_Atuador`, `ID_Fazenda`, `Status_Atual`, `Endereco_Logico`) VALUES
('Sistema de Irrigação Gotejador', 1, 2, 'Desligado', 'esp32/rele/irrigacao1');


-- 7. Registro de Leituras (Simulando uma mudança climática na Fazenda Sol Nascente)
INSERT INTO `registro_leituras` (`ID_Sensor`, `Valor_Leitura`, `Timestamp_Leitura`) VALUES
(1, '78.9', '2025-06-14 17:00:00'),
(2, '1005.1', '2025-06-14 17:00:00'),
-- Leitura que dispara o alerta
(1, '86.5', '2025-06-14 17:15:00'),
(2, '1002.3', '2025-06-14 17:15:00');

-- 8. Alerta (Gerado para a Fazenda Sol Nascente)
-- Note que o alerta está ligado à ID_Fazenda = 1.
INSERT INTO `alertas` (`ID_Fazenda`, `Timestamp_Emissao`, `Tipo_Alerta`, `Intensidade`, `Probabilidade`, `Mensagem`, `Status`, `Timestamp_Reconhecimento`, `ID_Usuario_Reconheceu`) VALUES
(1, '2025-06-14 17:18:00', 'Chuva Iminente', 'Severo', 85.00, 'Umidade Relativa acima do limite no Setor Norte.', 'Reconhecido', '2025-06-14 17:26:00', 2); -- Reconhecido por Maria (ID 2)

-- 9. Registro de Comandos (Ação tomada por Maria na Fazenda Sol Nascente)
-- Maria (ID_Usuario_Executor = 2) executa comandos nos atuadores da sua fazenda.
INSERT INTO `registro_comandos_atuadores` (`ID_Atuador`, `ID_Usuario_Executor`, `Comando_Executado`, `Timestamp_Comando`, `Status_Execucao`) VALUES
-- Comando para o atuador 1 (Ventilação Estufa)
(1, 2, 'FECHAR_VENTILACAO', '2025-06-14 17:27:00', 'Sucesso'),
-- Comando para o atuador 2 (Portão Celeiro)
(2, 2, 'FECHAR_PORTAO', '2025-06-14 17:28:00', 'Sucesso');