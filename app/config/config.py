"""
Configuration settings for the Flask application.
"""

class Config:
    """Base configuration class."""
    DEBUG = False
    SECRET_KEY = 'dev-key-change-in-production'  # Should be changed in production
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_alerta_chuvas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Opcional, mas recomendado para desativar avisos


    # MQTT Configuration
    MQTT_BROKER = 'fd2522b769fc4f16bb479a6cac3dcb7b.s1.eu.hivemq.cloud'
    MQTT_PORT = 8883
    MQTT_USERNAME = 'hivemq.webclient.1743567366904'
    MQTT_PASSWORD = '02DGadKA1Bb3fcCg.,;&'
    MQTT_TOPIC = 'sensor/dados'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # In production, you should set a strong secret key
    SECRET_KEY = 'production-secret-key'  # Should be set from environment variable


# Dictionary with different configuration environments
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}