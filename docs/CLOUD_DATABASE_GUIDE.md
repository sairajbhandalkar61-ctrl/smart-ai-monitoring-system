# SENTINEL AI — Cloud Database & Persistence Architecture

---

## 1. Multi-Engine Persistence Architecture

SENTINEL AI uses a universal database interface supporting both **PostgreSQL** in production cloud environments and **SQLite (WAL Mode)** for local offline execution.

```
       [DatabaseManager Interface]
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
[PostgreSQL (Cloud)]      [SQLite WAL (Local)]
  - Railway / Render        - data/sentinel.db
  - Connection Pooling      - High-concurrency WAL
  - Automatic Backups       - Zero external deps
```

---

## 2. Relational Schema & Tables

### 1. `users`
* `id` (Primary Key): Unique identifier
* `username` (Unique, Indexed): Account username
* `password_hash`: Hex-encoded PBKDF2 digest
* `salt`: 16-byte random salt
* `role`: User privilege (`admin`, `operator`, `viewer`)
* `created_at`: Unix timestamp

### 2. `edge_devices`
* `device_id` (Primary Key): E.g., `dell-edge-01`
* `device_name`: Human-readable device tag
* `device_token`: Pre-shared authentication token
* `last_heartbeat`: Timestamp of latest heartbeat signal
* `status`: `ONLINE` or `OFFLINE`
* `camera_source`: DirectShow interface identifier
* `cpu_percent`, `memory_mb`: Hardware telemetry
* `active_pipeline`: Integer boolean

### 3. `occupancy_telemetry`
* `id` (Primary Key)
* `timestamp` (Indexed): Measurement epoch
* `device_id`: Associated edge hardware node
* `camera_id`: Camera identifier
* `detected_count`: Raw detected persons
* `active_tracks`: Temporarily tracked count
* `tripwire_occupancy`: Reconciled facility headcount
* `entries`, `exits`: Tripwire cumulative crossings
* `activity_class`: "Low", "Moderate", "High Activity"
* `confidence`: Model probability
* `blur_score`, `brightness`: Visual quality metrics
* `is_reliable`: Reliability gate flag

### 4. `alerts`
* `id` (Primary Key)
* `timestamp` (Indexed)
* `device_id`: Originating hardware node
* `alert_type`: `high_occupancy`, `quality_warning`, etc.
* `severity`: `info`, `warning`, `high`, `critical`
* `title`, `description`: Incident narrative
* `zone_id`: Spatial zone
* `acknowledged`: Boolean status

---

## 3. Cloud Database Backups & Data Retention

* **Railway Automated Backups:** Railway automatically captures daily point-in-time snapshots of the PostgreSQL database.
* **Manual Export:** Facility managers can export all telemetry directly from the Streamlit dashboard on the **9. Historical Reports** page via the **📥 Download Historical Telemetry (CSV)** button.
