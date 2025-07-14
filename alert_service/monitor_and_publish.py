# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
import json
import mysql.connector
from pymongo import MongoClient
from neo4j import GraphDatabase
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", 2.0))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

print(f"[CONFIG] DROP_THRESHOLD = {DROP_THRESHOLD}")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["financial_data"]
forex_collection = mongo_db["forex_prices"]

mysql_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
mysql_cursor = mysql_conn.cursor()

neo_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

def insert_mysql_alert(alert):
    sql = """
    INSERT INTO alerts (currency, old_rate, new_rate, drop_percentage, alert_time)
    VALUES (%s, %s, %s, %s, %s)
    """
    vals = (
        alert["currency"],
        alert["old_rate"],
        alert["new_rate"],
        alert["drop_percentage"],
        alert["alert_time"]
    )
    mysql_cursor.execute(sql, vals)
    mysql_conn.commit()
    print(f"[MySQL] Inserted alert for {alert['currency']}")

def insert_neo4j_alert(alert):
    with neo_driver.session() as session:
        session.run(
            """
            MERGE (c:Currency {code: $currency})
            CREATE (a:Alert {
                old_rate: $old_rate,
                new_rate: $new_rate,
                drop_percentage: $drop_percentage,
                timestamp: datetime($alert_time)
            })
            MERGE (c)-[:HAS_ALERT]->(a)
            """,
            alert
        )
    print(f"[Neo4j] Alert node created for {alert['currency']}")

def publish_mqtt_alert(alert):
    topic = "forex/alerts"
    payload = json.dumps(alert)
    mqtt_client.publish(topic, payload)
    print(f"[MQTT] Published: {payload}")

def monitor_forex():
    while True:
        try:
            docs = list(forex_collection.find().sort("timestamp", -1).limit(2))
            if len(docs) < 2:
                print("Not enough data to compare yet.")
                time.sleep(CHECK_INTERVAL)
                continue

            latest, previous = docs[0], docs[1]
            alerts = []

            print(f"\n--- Comparing {latest['timestamp']} to {previous['timestamp']} ---")

            for currency, new_rate in latest["rates"].items():
                old_rate = previous["rates"].get(currency)
                if old_rate is None:
                    continue
                change_percent = ((new_rate - old_rate) / old_rate) * 100

                print(f"[{currency}] Old: {old_rate}, New: {new_rate}, Change: {change_percent:.5f}%")

                if abs(change_percent) >= DROP_THRESHOLD:
                    alert = {
                        "currency": currency,
                        "old_rate": old_rate,
                        "new_rate": new_rate,
                        "drop_percentage": change_percent,
                        "alert_time": latest["timestamp"]
                    }
                    alerts.append(alert)

            if alerts:
                print(f"\n[ALERT] {len(alerts)} alert(s) detected!")
                for alert in alerts:
                    insert_mysql_alert(alert)
                    insert_neo4j_alert(alert)
                    publish_mqtt_alert(alert)
            else:
                print("No alerts detected.")

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_forex()
