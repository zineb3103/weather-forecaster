import os
import json
import time
from datetime import datetime, timezone
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
    print("[producer] Streaming mode ON... (1 msg/sec)")
    producer = build_producer()
    topic = TOPICS['raw']

    try:
        while True:
            payload = fetch_payload()
            if not payload:
                print("[producer] No data fetched; skipping")
                time.sleep(1)
                continue

            timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            key = f"weather:{payload['metadata']['location']}:{timestamp}"

            future = producer.send(topic, key=key, value=payload)
            record_md = future.get(timeout=10)
            producer.flush()

            print(
                f"[producer] {timestamp} → "
                f"partition={record_md.partition} offset={record_md.offset}"
            )
            print(f"Key: {key}")
            print(f"Payload: {json.dumps(payload, indent=2)}\n")

            time.sleep(1)  # ⬅️ Stream every second

    except KeyboardInterrupt:
        print("\n⛔ Streaming stopped by user")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
