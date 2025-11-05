import os
import json
from datetime import datetime
from typing import Optional

from kafka import KafkaProducer

from backend.config.kafka_config import PRODUCER_CONFIG, TOPICS
from backend.ingestion.openmeteo_client import OpenMeteoClient


def get_coordinates() -> tuple[float, float]:
    lat = float(os.getenv("LATITUDE", 33.5731))
    lon = float(os.getenv("LONGITUDE", -7.5898))
    return lat, lon


def build_producer() -> KafkaProducer:
    return KafkaProducer(**PRODUCER_CONFIG)


def fetch_payload() -> Optional[dict]:
    lat, lon = get_coordinates()
    client = OpenMeteoClient(latitude=lat, longitude=lon)
    return client.get_current_weather()


def main() -> None:
    print("[producer] Starting...")
    payload = fetch_payload()
    if not payload:
        print("[producer] No data fetched; exiting")
        return

    topic = TOPICS['raw']
    key = f"weather:{payload['metadata']['location']}:{datetime.utcnow().isoformat()}"

    producer = build_producer()
    # Pass key as str; serializer handles encoding
    future = producer.send(topic, key=key, value=payload)
    record_md = future.get(timeout=10)
    producer.flush()
    print(f"[producer] Published to {topic} partition={record_md.partition} offset={record_md.offset}")


if __name__ == "__main__":
    main()


