# 📊 Sistema de Relatórios - StormGuard

## Visão Geral

O sistema de relatórios do StormGuard oferece uma análise avançada e visualização dos dados meteorológicos e alertas da sua fazenda. Com gráficos interativos, mapa de calor e exportação para PDF/Excel, você tem controle total sobre as informações do seu sistema.

## 🚀 Funcionalidades

### 📈 Gráficos Disponíveis

1. **Mapa de Calor das Áreas**
   - Visualização da intensidade de alertas por área da fazenda
   - Indicadores de tendência (crescimento/decréscimo)
   - Interativo: clique em uma área para filtrar dados

2. **Timeline de Alertas**
   - Gráfico de linha mostrando alertas ao longo do tempo
   - Alternância entre visualização de linha e barras
   - Filtros por período (24h, 7d, 30d)

3. **Distribuição de Intensidade**
   - Gráfico de rosca mostrando proporção de alertas por intensidade
   - Categorias: Leve, Moderado, Severo, Crítico

4. **Leituras dos Sensores por Hora**
   - Múltiplas linhas para diferentes tipos de sensores
   - Alternância entre temperatura, umidade, pressão
   - Dados em tempo real das últimas horas

5. **Status dos Dispositivos**
   - Gráfico de barras com status atual dos dispositivos IoT
   - Categorias: Ativo, Inativo, Manutenção

6. **Correlação Temperatura x Umidade**
   - Gráfico de dispersão (scatter plot)
   - Análise de correlação entre variáveis meteorológicas

7. **Qualidade das Leituras**
   - Gráfico de área empilhada
   - Categorias: Confiável, Ruído, Fora da Faixa

### 🎛️ Filtros Avançados

- **Período**: 24h, 7 dias, 30 dias, personalizado
- **Fazenda**: Filtrar por fazenda específica
- **Tipo de Sensor**: Filtrar por tipo de sensor
- **Área**: Filtrar por área específica (através do mapa de calor)

### 📊 Estatísticas Rápidas

Dashboard com métricas principais:
- Total de Alertas
- Alertas Críticos
- Sensores Ativos
- Média de Leituras por Hora

### 📄 Exportação

#### PDF
- Relatório completo com todos os gráficos
- Assinatura digital com hash SHA-256
- QR Code para verificação de autenticidade
- Layout profissional otimizado para impressão

#### Excel
- Dados tabulares para análise avançada
- Múltiplas abas organizadas por tipo de dados
- Formatação compatível com análises estatísticas

## 🛠️ Como Usar

### Acesso

1. Faça login no sistema StormGuard
2. Navegue para **Relatórios** no menu principal
3. A página carregará automaticamente com dados dos últimos 7 dias

### Navegação

1. **Aplicar Filtros**:
   - Selecione o período desejado
   - Escolha a fazenda (opcional)
   - Selecione o tipo de sensor (opcional)
   - Clique em "Aplicar Filtros"

2. **Interagir com Gráficos**:
   - Passe o mouse sobre elementos para ver detalhes
   - Clique em botões de alternância de tipo de gráfico
   - Use botões de exportação individual

3. **Exportar Relatório Completo**:
   - Role até o final da página
   - Clique em "Exportar PDF" ou "Exportar Excel"
   - O download iniciará automaticamente

### Mapa de Calor

- **Verde**: Baixa atividade de alertas (0-2)
- **Amarelo**: Atividade moderada (3-5)
- **Laranja**: Alta atividade (6-10)
- **Vermelho**: Atividade crítica (10+)

Indicadores de tendência:
- ↗ **Crescendo**: Aumento nos alertas
- ↘ **Diminuindo**: Redução nos alertas
- → **Estável**: Sem mudanças significativas

## 🔧 Configuração Técnica

### Estrutura de Arquivos

```
app/
├── templates/
│   └── relatorios.html          # Template principal
├── blueprints/main/
│   └── routes.py                # Rotas da API
├── static/
│   ├── relatorios.css          # Estilos específicos
│   └── script.js               # Scripts JavaScript
├── mock_data.py                # Dados de demonstração
└── models/                     # Modelos de dados
```

### Rotas da API

- `GET /relatorios` - Página principal
- `GET /api/reports/fazendas` - Lista de fazendas
- `GET /api/reports/tipos-sensor` - Tipos de sensores
- `POST /api/reports/quick-stats` - Estatísticas rápidas
- `POST /api/reports/heatmap` - Dados do mapa de calor
- `POST /api/reports/alerts-timeline` - Timeline de alertas
- `POST /api/reports/alerts-intensity` - Intensidade de alertas
- `POST /api/reports/sensor-readings` - Leituras dos sensores
- `POST /api/reports/device-status` - Status dos dispositivos
- `POST /api/reports/correlation` - Dados de correlação
- `POST /api/reports/quality` - Qualidade das leituras
- `POST /api/reports/export-full` - Exportação completa

### Dependências

#### Python
- Flask
- SQLAlchemy
- Pandas
- ReportLab (PDF)
- OpenPyXL (Excel)

#### JavaScript
- Chart.js
- Date-fns
- Bootstrap 5

## 📱 Responsividade

O sistema é totalmente responsivo e adaptado para:

- **Desktop**: Experiência completa com todos os gráficos
- **Tablet**: Layout adaptado com gráficos redimensionados
- **Mobile**: Interface otimizada com navegação simplificada

### Breakpoints

- **1200px+**: Layout completo
- **768px-1199px**: Layout médio com ajustes
- **480px-767px**: Layout móvel
- **<480px**: Layout extra pequeno

## 🎨 Tema Visual

### Paleta de Cores

- **Verde Neon**: `#33ff99` (destaque principal)
- **Verde Escuro**: `rgba(20, 22, 20, 0.85)` (fundos)
- **Texto Principal**: `#e8e8e8`
- **Texto Secundário**: `#a0a0a0`
- **Alerta**: `#ff4757`

### Animações

- **Entrada**: Slide-in com delay escalonado
- **Hover**: Transformações suaves
- **Loading**: Spinners e skeleton loaders
- **Pulse**: Indicadores de dados em tempo real

## 🚨 Tratamento de Erros

### Dados Insuficientes

Quando não há dados suficientes no banco, o sistema automaticamente:

1. Carrega dados mock realistas
2. Exibe aviso visual discreto
3. Mantém funcionalidade completa
4. Permite demonstração sem dados reais

### Falhas de Rede

- Retry automático em falhas temporárias
- Mensagens de erro amigáveis
- Fallback para dados em cache
- Indicadores visuais de estado

## 📚 Dados Mock

Para demonstração, o sistema inclui um gerador de dados realistas:

```bash
# Executar o script de dados de demonstração
python demo_data.py
```

### Dados Gerados

- 4 usuários de teste
- 3 fazendas com características diferentes
- 6 dispositivos IoT distribuídos
- 10 tipos de sensores
- 8 tipos de atuadores
- 7 dias de leituras históricas
- 30 dias de alertas
- 15 dias de comandos de atuadores

## 🔐 Segurança

### Autenticação

- Todas as rotas requerem login
- Verificação de sessão em cada requisição
- Tokens de segurança para exportação

### Verificação de Documentos

- Hash SHA-256 para integridade
- QR Code com URL de verificação
- Banco de registros de documentos
- Verificação pública sem login

### Proteção de Dados

- Sanitização de entrada
- Validação de parâmetros
- Logs de auditoria
- Rate limiting em APIs

## 🔧 Troubleshooting

### Problemas Comuns

1. **Gráficos não carregam**:
   - Verificar console do navegador
   - Confirmar conexão com backend
   - Verificar se há dados no banco

2. **Exportação falha**:
   - Verificar permissões de escrita
   - Confirmar bibliotecas instaladas
   - Verificar espaço em disco

3. **Performance lenta**:
   - Reduzir período de análise
   - Filtrar por fazenda específica
   - Verificar índices do banco

### Logs

Logs importantes são gravados em:
- Falhas de carregamento de dados
- Erros de exportação
- Problemas de conectividade
- Tentativas de acesso inválido

## 🚀 Futuras Melhorias

### Versão 2.0
- [ ] Dashboards personalizáveis
- [ ] Alertas em tempo real
- [ ] Integração com APIs meteorológicas
- [ ] Machine Learning para previsões
- [ ] App mobile nativo

### Versão 2.1
- [ ] Relatórios programados
- [ ] Notificações por email
- [ ] API REST pública
- [ ] Webhooks para integrações
- [ ] Multi-idioma

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte esta documentação
2. Verifique os logs da aplicação
3. Execute o script de dados de demonstração
4. Entre em contato com a equipe de desenvolvimento

---

**StormGuard** - Sistema Inteligente de Monitoramento Meteorológico  
*Desenvolvido com ❤️ para a agricultura brasileira*