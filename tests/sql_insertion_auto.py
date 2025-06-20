import pandas as pd
import numpy as np
import mysql.connector
import sys
from contextlib import contextmanager
from datetime import datetime

# --- CONFIGURAÇÕES ---
# Caminho para o seu arquivo CSV do INMET
import os
CSV_FILE_PATH = os.path.abspath('generatedBy_react-csv (22).csv')
# ID da Fazenda para a qual os sensores pertencem
# (com base no seu schema, os sensores INMET estão associados à ID_Fazenda = 1)
ID_FAZENDA = 1

# Configuração do banco de dados
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': 3306,
    'database': 'stormguard',
    'autocommit': False,
    'buffered': True,
    'consume_results': True,
    'connection_timeout': 30
}

# --- MAPEAMENTO DE COLUNAS DO CSV PARA IDs DOS SENSORES ---
# Este dicionário traduz os nomes das colunas do CSV para o ID_Sensor correspondente no seu banco de dados.
# Verifique se os nomes das colunas aqui correspondem exatamente aos do seu arquivo CSV.
# Os IDs dos sensores (valores) foram retirados da sua tabela `sensores`.
SENSOR_ID_MAP = {
    'Temp. Ins. (C)': 47,  # Temperatura instantânea
    'Umi. Ins. (%)': 48,   # Umidade instantânea
    'Pto Orvalho Ins. (C)': 41,  # Ponto de orvalho instantâneo
    'Pressao Ins. (hPa)': 40,    # Pressão instantânea
    'Vel. Vento (m/s)': 42,      # Velocidade do vento
    'Dir. Vento (m/s)': 43,      # Direção do vento
    'Raj. Vento (m/s)': 44,      # Rajada do vento
    'Radiacao (KJ/mÂ²)': 45      # Radiação
}

class DatabaseManager:
    def __init__(self, config):
        self.config = config

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            conn.autocommit = False
            yield conn
        except mysql.connector.Error as e:
            print(f"Erro ao conectar com MariaDB: {e}")
            if conn:
                conn.close()
            sys.exit(1)
        finally:
            if conn and conn.is_connected():
                conn.close()

    def execute_batch_insert(self, query, data_batch):
        """Execute batch insert for better performance"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor(buffered=True)
                cursor.executemany(query, data_batch)
                conn.commit()
                return cursor.rowcount
            except mysql.connector.Error as e:
                print(f"Erro ao executar batch insert: {e}")
                conn.rollback()
                return 0
            finally:
                if cursor:
                    cursor.close()

    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = None
                try:
                    cursor = conn.cursor(buffered=True)
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchall()  # Consume all results
                    print("✓ Conexão com banco de dados testada com sucesso!")
                    return True
                finally:
                    if cursor:
                        cursor.close()
        except Exception as e:
            print(f"✗ Erro na conexão com banco de dados: {e}")
            return False

    def check_duplicate_records(self, sensor_id, timestamp_start, timestamp_end):
        """Check if there are existing records for a sensor in the given time range"""
        query = """
        SELECT COUNT(*) FROM registro_leituras
        WHERE ID_Sensor = %s AND Timestamp_Leitura BETWEEN %s AND %s
        """
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor(buffered=True)
                cursor.execute(query, (sensor_id, timestamp_start, timestamp_end))
                result = cursor.fetchone()
                count = result[0] if result else 0
                return count
            finally:
                if cursor:
                    cursor.close()

def processar_dados_e_inserir_no_banco():
    """
    Função principal que lê o CSV, processa todos os dados e insere
    diretamente no banco de dados MariaDB.
    """

    # Inicializar o gerenciador de banco de dados
    db_manager = DatabaseManager(DB_CONFIG)

    print("🔄 Testando conexão com banco de dados...")
    # Testar conexão
    if not db_manager.test_connection():
        print("Abortando devido a problemas de conexão com o banco de dados.")
        return

    try:
        # Tenta ler o arquivo CSV.
        # skiprows=8: Pula as 8 linhas de cabeçalho do arquivo do INMET.
        # sep=';': Define o ponto e vírgula como separador de colunas.
        # decimal=',': Define a vírgula como separador decimal.
        # encoding='latin-1': Codificação comum para arquivos gerados no Brasil.
        print(f"📄 Tentando ler arquivo: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH, sep=';', decimal=',', encoding='latin-1')
        print(f"✓ Arquivo '{CSV_FILE_PATH}' lido com sucesso.")
        print(f"✓ Total de linhas no arquivo: {len(df)}")

    except FileNotFoundError:
        print(f"✗ ERRO: O arquivo '{CSV_FILE_PATH}' não foi encontrado.")
        print("Por favor, verifique se o nome e o caminho do arquivo estão corretos.")
        return
    except Exception as e:
        print(f"✗ Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return

    # --- LIMPEZA E PREPARAÇÃO DOS DADOS ---

    # Remove a última coluna, que geralmente está vazia ou é inútil nos arquivos do INMET
    df = df.iloc[:, :-1]

    # Substitui os valores -9999 (padrão do INMET para dados ausentes) por NaN (Not a Number)
    df.replace(-9999, np.nan, inplace=True)

    print(f"📊 Colunas originais do CSV: {list(df.columns)}")

    # Renomeia colunas para facilitar o acesso
    # Remove os caracteres BOM no início da primeira coluna
    df.columns = df.columns.str.replace('ï»¿"', '', regex=False)
    df.columns = df.columns.str.replace('"', '', regex=False)
    
    df.rename(columns={
        'Data': 'data',
        'Hora (UTC)': 'hora',
    }, inplace=True)

    # Remove o sufixo ' (UTC)' da coluna de hora, se existir
    if 'hora' in df.columns:
        df['hora'] = df['hora'].astype(str).str.replace(' (UTC)', '', regex=False).str.zfill(4)
    else:
        print("✗ Coluna 'hora' não encontrada após renomeação. Verifique o CSV.")
        return

    # Renomeia as colunas de dados para remover espaços e caracteres especiais para facilitar o acesso
    # Ex: 'PRECIPITACAO TOTAL, HORARIO (mm)' vira 'PRECIPITACAO_TOTAL_HORARIO_mm'
    df.columns = [col.upper().replace(' (° (GR))', '').replace(' (°C)', '').replace(' (KJ/M²)', '').replace(' (M/S)', '').replace(' (MM)', '').replace(' (MB)', '').replace(' (%)', '').replace(',', '').replace(' ', '_').replace('-', '_') for col in df.columns]

    # Atualiza as chaves do dicionário de mapeamento para corresponder às colunas renomeadas
    cleaned_sensor_map = {key.upper().replace(' (° (GR))', '').replace(' (°C)', '').replace(' (KJ/M²)', '').replace(' (M/S)', '').replace(' (MM)', '').replace(' (MB)', '').replace(' (%)', '').replace(',', '').replace(' ', '_').replace('-', '_'): value for key, value in SENSOR_ID_MAP.items()}

    print(f"🔗 Mapeamento de sensores:")
    for col_name, sensor_id in cleaned_sensor_map.items():
        if col_name in df.columns:
            print(f"   ✓ {col_name} -> Sensor ID {sensor_id}")
        else:
            print(f"   ✗ {col_name} (não encontrada no CSV)")

    # Combina as colunas de data e hora em uma única coluna de timestamp
    try:
        # Garante que a hora está no formato HH:MM
        df['HORA'] = df['HORA'].str.slice(0, 2) + ':' + df['HORA'].str.slice(2, 4)
        # Converte a data do formato DD/MM/YYYY para YYYY/MM/DD
        df['timestamp'] = pd.to_datetime(df['DATA'] + ' ' + df['HORA'], format='%d/%m/%Y %H:%M')
    except Exception as e:
        print(f"✗ Erro ao converter data e hora. Verifique o formato no CSV. Erro: {e}")
        return

    df.sort_values('timestamp', inplace=True)

    # --- VERIFICAÇÃO DE DUPLICATAS ---
    first_timestamp = df['timestamp'].min()
    last_timestamp = df['timestamp'].max()
    print(f"📅 Período dos dados: {first_timestamp} até {last_timestamp}")

    print("🔍 Verificando registros existentes...")
    # Verificar se já existem dados para este período
    for sensor_id in list(cleaned_sensor_map.values())[:1]:  # Verificar apenas um sensor para economizar tempo
        duplicate_count = db_manager.check_duplicate_records(sensor_id, first_timestamp, last_timestamp)
        if duplicate_count > 0:
            response = input(f"⚠️  Encontrados {duplicate_count} registros existentes para o sensor {sensor_id} neste período. Continuar mesmo assim? (s/n): ")
            if response.lower() != 's':
                print("Operação cancelada pelo usuário.")
                return
        break

    # --- INSERÇÃO NO BANCO DE DADOS ---

    total_records = len(df)
    print(f"💾 Preparando inserção de {total_records} linhas de dados horários no banco de dados.")

    # Preparar dados para inserção em lote
    insert_data = []

    # Query de inserção
    insert_query = """
    INSERT INTO registro_leituras
    (ID_Sensor, Valor_Leitura, Timestamp_Leitura, Qualidade)
    VALUES (%s, %s, %s, %s)
    """

    # Contar registros processados
    records_processed = 0
    records_skipped = 0
    batch_size = 500  # Reduzir tamanho do lote para melhor estabilidade

    print("🚀 Iniciando processamento dos dados...")

    # Itera sobre cada linha do dataframe
    for index, row in df.iterrows():
        timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        # Itera sobre o nosso mapa de sensores para criar um INSERT para cada leitura
        for col_name, sensor_id in cleaned_sensor_map.items():
            if col_name in df.columns:
                valor_leitura = row[col_name]

                # Só insere se o valor da leitura for válido (não for NaN)
                if pd.notna(valor_leitura):
                    insert_data.append((sensor_id, float(valor_leitura), timestamp_str, 'Confiavel'))
                else:
                    records_skipped += 1

        # Inserir em lotes para melhor performance
        if len(insert_data) >= batch_size:
            rows_inserted = db_manager.execute_batch_insert(insert_query, insert_data)
            records_processed += rows_inserted
            print(f"✓ Inseridos {records_processed} registros no banco de dados...")
            insert_data = []  # Limpar o lote

        # Mostrar progresso a cada 50 linhas processadas
        if (index + 1) % 50 == 0:
            progress = ((index + 1) / total_records) * 100
            print(f"📊 Progresso: {progress:.1f}% ({index + 1}/{total_records} linhas processadas)")

    # Inserir registros restantes
    if insert_data:
        rows_inserted = db_manager.execute_batch_insert(insert_query, insert_data)
        records_processed += rows_inserted

    print(f"\n🎉 Inserção concluída com sucesso!")
    print(f"✅ Registros inseridos: {records_processed}")
    print(f"⏭️  Registros ignorados (valores nulos): {records_skipped}")
    print(f"🗄️  Banco: {DB_CONFIG['database']}")
    print(f"🌐 Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("✅ Todos os dados foram importados com sucesso!")

if __name__ == "__main__":
    # Verificar se o módulo mysql.connector está instalado
    try:
        import mysql.connector
    except ImportError:
        print("✗ ERRO: O módulo 'mysql-connector-python' não está instalado.")
        print("Para instalar, execute: pip install mysql-connector-python")
        sys.exit(1)

    # Verificar se o pandas está instalado
    try:
        import pandas as pd
    except ImportError:
        print("✗ ERRO: O módulo 'pandas' não está instalado.")
        print("Para instalar, execute: pip install pandas")
        sys.exit(1)

    print("=" * 60)
    print("  🌦️  IMPORTADOR DE DADOS INMET PARA BANCO STOMGUARD")
    print("=" * 60)
    print(f"Iniciando processamento em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Executar o processamento e inserção
    processar_dados_e_inserir_no_banco()

    print("=" * 60)
    print(f"Processamento finalizado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
