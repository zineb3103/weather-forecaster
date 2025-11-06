import os
import time
from datetime import datetime, timezone
from typing import Optional

from kafka import KafkaProducer
from backend.config.kafka_config import PRODUCER_CONFIG, TOPICS
from backend.ingestion.openmeteo_client import OpenMeteoClient


class WeatherProducer:
    def __init__(self):
        self.producer = KafkaProducer(**PRODUCER_CONFIG)
        lat = float(os.getenv("LATITUDE", 33.5731))
        lon = float(os.getenv("LONGITUDE", -7.5898))
        self.client = OpenMeteoClient(latitude=lat, longitude=lon)
        self.poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", 300))  # 5 min par défaut
    
    def fetch_payload(self) -> Optional[dict]:
        """Récupère les données météo"""
        return self.client.get_current_weather()
    
    def run(self):
        print(f"🌤️  Weather Producer démarré (poll every {self.poll_interval}s)")
        topic = TOPICS['raw']
        
        try:
            while True:
                payload = self.fetch_payload()
                
                if payload:
                    timestamp = datetime.now(timezone.utc).isoformat()
                    key = f"weather:{payload['metadata']['location']}:{timestamp}"
                    
                    future = self.producer.send(topic, key=key, value=payload)
                    record_md = future.get(timeout=10)
                    
                    print(f"✅ [{timestamp[:19]}] → partition={record_md.partition} "
                          f"offset={record_md.offset} | "
                          f"Temp={payload['current']['temperature_2m']}°C")
                else:
                    print("⚠️  Aucune donnée récupérée")
                
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\n⛔ Producer arrêté")
        finally:
            self.producer.close()


if __name__ == "__main__":
    producer = WeatherProducer()
    producer.run()