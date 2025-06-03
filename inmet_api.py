from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import paho.mqtt.client as mqtt
import json
import time

# Set up Chrome options for automatic downloads
chrome_options = Options()
prefs = {
    "download.default_directory": "./",  # Change this to your desired path
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Open the webpage
    driver.get("https://tempo.inmet.gov.br/TabelaEstacoes/A807")  # Replace with the actual URL

    # Wait for the page to load
    time.sleep(5)

    # Find and click the button to download CSV
    download_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Baixar CSV')]")  # Adjust selector as needed
    ActionChains(driver).move_to_element(download_button).click().perform()

    # Wait for download to complete
    time.sleep(5)
finally:
    driver.quit()

# --- Configuration ---
CSV_FILE_PATH = 'generatedBy_react-csv.csv'  # Replace with your actual CSV file path
MQTT_BROKER_HOST = 'localhost'  # Replace with your MQTT broker's address
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = 'inmet/data/filtered' # Choose a relevant topic name

# Columns to EXCLUDE (Update these with the EXACT names from your CSV header)
COLUMNS_TO_EXCLUDE = [
    'Temp. Ins. (C)', 'Temp. Max. (C)', 'Temp. Min. (C)',
    'Umi. Ins. (%)', 'Umi. Max. (%)', 'Umi. Min. (%)'
]

# --- Functions ---

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Conectado ao Broker MQTT: {MQTT_BROKER_HOST}")
    else:
        print(f"Falha ao conectar, código de retorno: {rc}")

def on_publish(client, userdata, mid, properties=None, reason_code=None):
    # Older paho-mqtt versions might not have properties/reason_code
    # You can simplify to on_publish(client, userdata, mid)
    print(f"Mensagem Publicada MID: {mid}")

def process_and_publish_inmet_data():
    """
    Lê dados do CSV do INMET, filtra temperatura e umidade,
    e publica os dados restantes via MQTT HiveMQ Cloud.
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH, delimiter=';')
        print("CSV lido com sucesso. Colunas encontradas:")
        print(df.columns.tolist())

        all_columns = df.columns.tolist()
        columns_to_send = [col for col in all_columns if col not in COLUMNS_TO_EXCLUDE]

        if not columns_to_send:
            print("Nenhuma coluna selecionada para envio. Verifique os nomes em COLUMNS_TO_EXCLUDE.")
            return

        print(f"\nColunas que serão enviadas para o MQTT (sensor/dados):")
        print(columns_to_send)

        df_filtered = df[columns_to_send]
        print("\nPrimeiras linhas dos dados que serão enviados:")
        print(df_filtered.head())

        # Remove linhas com NaN nas colunas selecionadas
        df_filtered = df_filtered.dropna(how='any')
        if df_filtered.empty:
            print("Nenhum dado disponível para envio (todos os registros possuem valores ausentes).")
            return

        # Seleciona o último registro disponível
        last_row = df_filtered.iloc[[-1]]
        print("\nÚltimo registro disponível para envio:")
        print(last_row)

        # --- Configuração do MQTT HiveMQ Cloud ---
        HIVEMQ_HOST = "fd2522b769fc4f16bb479a6cac3dcb7b.s1.eu.hivemq.cloud"
        HIVEMQ_PORT = 8883
        HIVEMQ_USER = "hivemq.webclient.1743567366904"
        HIVEMQ_PASS = "02DGadKA1Bb3fcCg.,;&"
        MQTT_TOPIC = "inmet/dados"

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("Conectado ao HiveMQ com sucesso!")
            else:
                print(f"Falha na conexão. Código de retorno: {rc}")

        def on_publish(client, userdata, mid):
            print(f"Mensagem publicada com ID: {mid}")

        import ssl
        client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT)
        client.loop_start()

        # Envia apenas o último registro disponível
        dados = last_row.iloc[0].to_dict()
        json_dados = json.dumps(dados, ensure_ascii=False)
        print(json_dados)
        result = client.publish(MQTT_TOPIC, json_dados, qos=1)
        result.wait_for_publish()
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Enviado ao HiveMQ: {json_dados}")
        else:
            print(f"Falha ao enviar mensagem: {mqtt.error_string(result.rc)}")
        time.sleep(0.1)

        client.loop_stop()
        client.disconnect()
        print("\nProcessamento e envio concluídos.")

    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em '{CSV_FILE_PATH}'")
    except pd.errors.EmptyDataError:
        print(f"Erro: Arquivo CSV '{CSV_FILE_PATH}' está vazio.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Main Execution ---
if __name__ == '__main__':
    # First, let's inspect the CSV headers provided by the user.
    try:
        df_inspect = pd.read_csv('generatedBy_react-csv.csv', delimiter=';', nrows=0) # Read only headers
        print("--- Cabeçalhos do CSV fornecido ('generatedBy_react-csv.csv') ---")
        print(df_inspect.columns.tolist())
        print("------------------------------------------------------------------")
        print("\nIMPORTANTE: Atualize a lista 'COLUMNS_TO_EXCLUDE' no script com os nomes exatos das colunas de umidade e temperatura do seu CSV.\n")
    except Exception as e:
        print(f"Não foi possível ler os cabeçalhos do CSV 'generatedBy_react-csv.csv': {e}")
        print("Certifique-se de que o arquivo está no mesmo diretório ou forneça o caminho completo.")

    print("\nIniciando o processo de envio de dados INMET (excluindo temperatura e umidade)...")
    process_and_publish_inmet_data()