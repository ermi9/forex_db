import streamlit as st
from neo4j import GraphDatabase
import pandas as pd

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "strongpass123"  
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_alerts():
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Alert)
            RETURN a.currency AS currency, a.old_rate AS old_rate, 
                   a.new_rate AS new_rate, a.drop_percentage AS drop_percentage, 
                   a.alert_time AS alert_time
            ORDER BY a.alert_time DESC
            LIMIT 50
        """)
        return pd.DataFrame([record.data() for record in result])

# Streamlit UI
st.title("📉 Forex Alerts Viewer")

st.write("Latest alerts from Neo4j:")

df = get_alerts()

if df.empty:
    st.info("No alerts found yet.")
else:
    st.dataframe(df)

# Optional: auto-refresh
if st.button("🔄 Refresh Alerts"):
    df = get_alerts()
    st.dataframe(df)
