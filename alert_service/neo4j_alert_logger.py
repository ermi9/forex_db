import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise EnvironmentError("Missing Neo4j connection credentials in .env file.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def log_alert(currency, drop_percentage, old_rate, new_rate):
    timestamp = datetime.utcnow().isoformat()
    with driver.session() as session:
        session.write_transaction(_create_alert_node, currency, drop_percentage, old_rate, new_rate, timestamp)

def _create_alert_node(tx, currency, drop, old_rate, new_rate, timestamp):
    tx.run("""
        MERGE (c:Currency {code: $currency})
        CREATE (a:Alert {
            drop_percentage: $drop,
            old_rate: $old_rate,
            new_rate: $new_rate,
            timestamp: $timestamp
        })
        MERGE (a)-[:ABOUT]->(c)
    """, currency=currency, drop=drop, old_rate=old_rate, new_rate=new_rate, timestamp=timestamp)

if __name__ == "__main__":
    # Example test
    log_alert("EUR", 2.5, 1.10, 1.07)
    print("Alert logged to Neo4j.")
