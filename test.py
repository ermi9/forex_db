from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "strongpass123"  # your neo4j password here

driver = GraphDatabase.driver(uri, auth=(user, password))

def fetch_alerts(tx):
    query = """
    MATCH (a:Alert)
    RETURN a
    ORDER BY a.alert_time DESC
    LIMIT 100
    """
    return list(tx.run(query))

with driver.session() as session:
    alerts = session.read_transaction(fetch_alerts)
    for record in alerts:
        alert_node = record["a"]
        print(dict(alert_node))  # print all properties as a dictionary

driver.close()
