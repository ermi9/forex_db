# 💱 Forex_DB Project

A multi-database backend that tracks live forex and crypto prices, detects big changes, and sends alerts using multiple data stores.

---

## 🔍 What It Does

- **Fetches** live forex/crypto prices from an external API.
- **Stores** the data in **MongoDB**.
- **Analyzes** price changes to spot sudden drops or spikes.
- **Sends alerts** when thresholds are crossed:
  - Stores alert logs in **MySQL**
  - Models relationships in **Neo4j**
  - (Optional) Publishes alerts over MQTT

---

## 🧩 How It Works

```
[API] → [MongoDB (raw prices)]
         ↓
   [Change detection logic]
         ↓
[MySQL (alert logs)] + [Neo4j (asset relationships)]
```

🏁 How to Run
Make sure Docker and Docker Compose are installed.

1. Clone the repo:

```   
  git clone https://github.com/yourusername/forex_db.git
  cd forex_db
```
2.Start the system:
```
docker-compose up --build
