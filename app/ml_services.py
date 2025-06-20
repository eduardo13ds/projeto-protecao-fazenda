import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from catboost import CatBoostRegressor
from flask import current_app
from app.extensions import db
from app.models.registro_leitura import RegistroLeitura
from app.models.sensor import Sensor
from app.models.tipo_sensor import TipoSensor

# Mapeamento dos tipos de sensor para os nomes esperados pelo modelo
# Baseado nos nomes dos tipos de sensor que você provavelmente tem no banco
SENSOR_TYPE_MAP = {
    'temperatura': 'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
    'umidade': 'UMIDADE RELATIVA DO AR, HORARIA (%)',
    'pressao': 'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
    'velocidade_vento': 'VENTO, VELOCIDADE HORARIA (m/s)',
    'direcao_vento': 'VENTO, DIREÇÃO HORARIA (gr) (° (gr))',
    'precipitacao': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
    'ponto_orvalho': 'TEMPERATURA DO PONTO DE ORVALHO (°C)'
}

class PredictionService:
    _model = None
    _model_features = None

    @classmethod
    def get_model(cls):
        """Carrega o modelo de ML se ainda não estiver carregado."""
        if cls._model is not None:
            if cls._model_features is None:
                cls._model_features = cls._model.feature_names_
            return cls._model

        try:
            # Caminho para o modelo (ajuste conforme necessário)
            model_path = os.path.join(current_app.root_path, 'ml_models', 'precipitation_model.cbm')

            if not os.path.exists(model_path):
                current_app.logger.error(f"Modelo não encontrado em: {model_path}")
                return None

            cls._model = CatBoostRegressor()
            cls._model.load_model(model_path)
            cls._model_features = cls._model.feature_names_

            current_app.logger.info("Modelo de ML carregado com sucesso!")
            return cls._model

        except Exception as e:
            current_app.logger.error(f"Erro ao carregar modelo de ML: {e}")
            return None

    @classmethod
    def prepare_features_for_prediction(cls, area_id=None):
        """Prepara as features para previsão baseado nos dados históricos."""
        current_app.logger.info(f"Iniciando preparação de features para área: {area_id}")
        
        model = cls.get_model()
        if not model:
            current_app.logger.error("Modelo não carregado durante preparação de features")
            raise RuntimeError("Modelo de ML não está carregado.")

        # 1. Buscar dados históricos das últimas 25 horas
        cutoff_time = datetime.utcnow() - timedelta(hours=25)
        current_app.logger.info(f"Buscando dados desde: {cutoff_time}")

        # Query corrigida usando os nomes corretos dos atributos
        try:
            query = db.session.query(
                RegistroLeitura.timestamp_leitura.label('timestamp'),
                RegistroLeitura.valor_leitura.label('valor'),
                TipoSensor.nome_tipo.label('tipo_sensor_nome')
            ).join(
                Sensor, RegistroLeitura.id_sensor == Sensor.id_sensor
            ).join(
                TipoSensor, Sensor.id_tipo_sensor == TipoSensor.id_tipo_sensor
            ).filter(
                RegistroLeitura.timestamp_leitura >= cutoff_time
            )

            if area_id:
                query = query.filter(Sensor.id_fazenda == area_id)

            # Log query for debugging
            current_app.logger.debug(f"SQL Query: {query}")
            
            # Executar query e converter para DataFrame
            long_df = pd.read_sql(query.statement, db.engine)
            current_app.logger.info(f"Dados recuperados: {len(long_df)} registros")
            
            if long_df.empty:
                current_app.logger.warning("Nenhum dado encontrado para o período")
                return None

            current_app.logger.info(f"Tipos de sensores encontrados: {long_df['tipo_sensor_nome'].unique()}")
            
        except Exception as e:
            current_app.logger.error(f"Erro ao executar query: {e}")
            return None

        # 2. Converter valores para float
        try:
            long_df['valor'] = pd.to_numeric(long_df['valor'], errors='coerce')
            long_df = long_df.dropna(subset=['valor'])
        except Exception as e:
            current_app.logger.error(f"Erro ao converter valores para float: {e}")
            return None

        # 3. Mapear tipos de sensor para nomes esperados pelo modelo
        long_df['tipo_sensor_modelo'] = long_df['tipo_sensor_nome'].str.lower().map(SENSOR_TYPE_MAP)
        long_df = long_df.dropna(subset=['tipo_sensor_modelo'])

        if long_df.empty:
            current_app.logger.warning("Nenhum tipo de sensor mapeado encontrado.")
            return None

        # 4. Pivotar dados para formato largo
        try:
            wide_df = long_df.pivot_table(
                index='timestamp',
                columns='tipo_sensor_modelo',
                values='valor',
                aggfunc='mean'
            )

            # Resample para dados horários
            wide_df = wide_df.resample('H').mean()

            # Preencher valores ausentes
            wide_df = wide_df.fillna(method='ffill').fillna(method='bfill')

        except Exception as e:
            current_app.logger.error(f"Erro ao pivotar dados: {e}")
            return None

        # 5. Aplicar engenharia de features
        try:
            df = cls._apply_feature_engineering(wide_df)
        except Exception as e:
            current_app.logger.error(f"Erro na engenharia de features: {e}")
            return None

        # 6. Selecionar última linha e features corretas
        if df.empty:
            current_app.logger.warning("DataFrame vazio após engenharia de features.")
            return None

        latest_features = df.tail(1)

        # Garantir que temos as features que o modelo espera
        missing_features = set(cls._model_features) - set(latest_features.columns)
        if missing_features:
            current_app.logger.warning(f"Features ausentes: {missing_features}")
            # Adicionar features ausentes com valor 0
            for feature in missing_features:
                latest_features[feature] = 0

        # Selecionar e ordenar features conforme o modelo
        latest_features = latest_features[cls._model_features]

        # Tratar NaNs
        latest_features = latest_features.fillna(0)

        current_app.logger.info(f"Features preparadas para previsão: {latest_features.values}")
        return latest_features

    @classmethod
    def _apply_feature_engineering(cls, df):
        """Aplica engenharia de features nos dados."""

        # Configuração para lags, rolling windows, etc.
        feature_config = {
            "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": {
                "lags": [1, 2, 3, 24],
                "rolling_sums": [3, 6],
                "prefix": "PREC"
            },
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": {
                "lags": [1, 2, 3, 24],
                "prefix": "TEMP_AR"
            },
            "UMIDADE RELATIVA DO AR, HORARIA (%)": {
                "lags": [1, 2, 3, 24],
                "prefix": "UMID_REL"
            },
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": {
                "lags": [1, 2, 3, 24],
                "diffs": [3],
                "prefix": "PRESSAO"
            },
            "VENTO, VELOCIDADE HORARIA (m/s)": {
                "lags": [1, 2],
                "prefix": "VENTO_VEL"
            },
            "VENTO, DIREÇÃO HORARIA (gr) (° (gr))": {
                "lags": [1],
                "prefix": "VENTO_DIR"
            },
            "TEMPERATURA DO PONTO DE ORVALHO (°C)": {
                "lags": [1, 2, 24],
                "prefix": "TEMP_ORV"
            }
        }

        # Aplicar transformações
        for col_name, config in feature_config.items():
            if col_name not in df.columns:
                continue

            prefix = config["prefix"]

            # Lags
            for lag in config.get("lags", []):
                df[f'{prefix}_lag_{lag}h'] = df[col_name].shift(lag)

            # Rolling sums
            for window in config.get("rolling_sums", []):
                df[f'{prefix}_soma_ultimas_{window}h'] = df[col_name].shift(1).rolling(window=window).sum()

            # Differences
            for lag_diff in config.get("diffs", []):
                df[f'{prefix}_diff_{lag_diff}h'] = df[col_name].diff(periods=lag_diff)

        # Features temporais
        df = df.reset_index()
        df['Timestamp'] = pd.to_datetime(df['timestamp'])

        df['HORA'] = df['Timestamp'].dt.hour
        df['DIA_DA_SEMANA'] = df['Timestamp'].dt.dayofweek
        df['DIA_DO_MES'] = df['Timestamp'].dt.day
        df['MES'] = df['Timestamp'].dt.month
        df['DIA_DO_ANO'] = df['Timestamp'].dt.dayofyear

        # Componentes cíclicos
        df['HORA_sin'] = np.sin(2 * np.pi * df['HORA'] / 24)
        df['HORA_cos'] = np.cos(2 * np.pi * df['HORA'] / 24)
        df['DIA_DO_ANO_sin'] = np.sin(2 * np.pi * df['DIA_DO_ANO'] / 365.25)
        df['DIA_DO_ANO_cos'] = np.cos(2 * np.pi * df['DIA_DO_ANO'] / 365.25)
        df['MES_sin'] = np.sin(2 * np.pi * (df['MES'] - 1) / 12)
        df['MES_cos'] = np.cos(2 * np.pi * (df['MES'] - 1) / 12)
        df['DIA_DA_SEMANA_sin'] = np.sin(2 * np.pi * df['DIA_DA_SEMANA'] / 7)
        df['DIA_DA_SEMANA_cos'] = np.cos(2 * np.pi * df['DIA_DA_SEMANA'] / 7)

        # Remover colunas de timestamp
        df = df.drop(['timestamp', 'Timestamp'], axis=1, errors='ignore')

        return df

    @classmethod
    def predict(cls, area_id=None):
        """Gera uma previsão mock baseada em dados das últimas 24 horas."""
        try:
            current_app.logger.info(f"Gerando previsão mock para área {area_id}")
            
            # Gerar um valor base entre 0 e 15mm
            base_prediction = np.random.uniform(0, 15)
            
            # Hora atual
            current_hour = datetime.now().hour
            
            # Ajustar previsão com base na hora do dia
            # Maior probabilidade de chuva no final da tarde (15-18h)
            if 15 <= current_hour <= 18:
                base_prediction *= 1.5
            # Menor probabilidade de chuva pela manhã (6-9h)
            elif 6 <= current_hour <= 9:
                base_prediction *= 0.5
                
            # Adicionar um pouco de variação por área
            if area_id is not None:
                area_factor = (area_id % 3 + 1) * 0.2  # 0.2, 0.4, ou 0.6
                base_prediction *= (1 + area_factor)
            
            mock_prediction = round(base_prediction, 1)
            current_app.logger.info(f"Previsão mock gerada: {mock_prediction}mm para hora {current_hour}")
            return mock_prediction
        except Exception as e:
            current_app.logger.error(f"Erro ao gerar previsão mock: {str(e)}")
            return None
