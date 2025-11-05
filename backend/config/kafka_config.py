"""Configuration Kafka pour le projet Weather Forecaster"""

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

# Topics
TOPICS = {
    'raw': 'data.raw.weather',
    'cleaned': 'data.cleaned.weather',
    'features': 'data.features.weather',
    'predictions': 'data.predictions.weather'
}

# Producer Configuration
PRODUCER_CONFIG = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,
    'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
    'key_serializer': lambda k: k.encode('utf-8') if k else None,
    'acks': 'all',  # Attendre confirmation de tous les replicas
    'retries': 3,
    'max_in_flight_requests_per_connection': 1  # Garantir l'ordre
}

# Consumer Configuration
CONSUMER_CONFIG = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,
    'value_deserializer': lambda v: json.loads(v.decode('utf-8')),
    'key_deserializer': lambda k: k.decode('utf-8') if k else None,
    'auto_offset_reset': 'earliest',
    'enable_auto_commit': True,
    'group_id': 'weather-processing-group'
}

import json