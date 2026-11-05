import os
import time
import hashlib
import secrets
import sqlite3
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "sentinel.db")

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, stored_hash)

class DatabaseManager:
    """
    Universal Database Persistence Manager for SENTINEL AI.
    Seamlessly supports PostgreSQL (Cloud Production) and SQLite (Local Edge).
    """
    def __init__(self, database_url: Optional[str] = None):
        self.url = database_url or os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
        self.is_postgres = self.url.startswith("postgres://") or self.url.startswith("postgresql://")
        
        if not self.is_postgres:
            # Clean sqlite:/// prefix if present
            if self.url.startswith("sqlite:///"):
                self.sqlite_path = self.url.replace("sqlite:///", "")
            else:
                self.sqlite_path = DB_PATH
            os.makedirs(os.path.dirname(os.path.abspath(self.sqlite_path)), exist_ok=True)
            self._init_sqlite()
        else:
            self._init_postgres()

    def _get_connection(self):
        if self.is_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            # Railway sometimes uses postgres:// which psycopg2 prefers as postgresql://
            pg_url = self.url
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(self.sqlite_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            return conn

    def _init_sqlite(self):
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")

        # 1. Users Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            created_at REAL NOT NULL
        );
        """)

        # 2. Edge Devices Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS edge_devices (
            device_id TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            device_token TEXT NOT NULL,
            last_heartbeat REAL NOT NULL,
            status TEXT NOT NULL,
            camera_source TEXT,
            cpu_percent REAL DEFAULT 0.0,
            memory_mb REAL DEFAULT 0.0,
            active_pipeline INTEGER DEFAULT 0,
            created_at REAL NOT NULL
        );
        """)

        # 3. Occupancy Telemetry Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS occupancy_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            device_id TEXT DEFAULT 'dell-edge-01',
            camera_id TEXT NOT NULL,
            detected_count INTEGER NOT NULL,
            active_tracks INTEGER NOT NULL,
            tripwire_occupancy INTEGER NOT NULL,
            entries INTEGER NOT NULL,
            exits INTEGER NOT NULL,
            activity_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            blur_score REAL,
            brightness REAL,
            is_reliable INTEGER NOT NULL
        );
        """)

        # 4. Alerts Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            device_id TEXT DEFAULT 'dell-edge-01',
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            zone_id TEXT,
            acknowledged INTEGER DEFAULT 0
        );
        """)

        # 5. System Health Logs
        cur.execute("""
        CREATE TABLE IF NOT EXISTS system_health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            device_id TEXT DEFAULT 'dell-edge-01',
            fps REAL NOT NULL,
            latency_ms REAL NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_mb REAL NOT NULL,
            camera_status TEXT NOT NULL
        );
        """)

        # Migrations for existing tables
        cur.execute("PRAGMA table_info(occupancy_telemetry);")
        cols = [col[1] for col in cur.fetchall()]
        if "device_id" not in cols:
            cur.execute("ALTER TABLE occupancy_telemetry ADD COLUMN device_id TEXT DEFAULT 'dell-edge-01';")

        cur.execute("PRAGMA table_info(alerts);")
        alert_cols = [col[1] for col in cur.fetchall()]
        if "device_id" not in alert_cols:
            cur.execute("ALTER TABLE alerts ADD COLUMN device_id TEXT DEFAULT 'dell-edge-01';")

        # Indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_time ON occupancy_telemetry(timestamp);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_device ON occupancy_telemetry(device_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp);")

        # Seed Default Admin if none exists
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            h, s = hash_password("SentinelAdmin2026!")
            cur.execute(
                "INSERT INTO users (username, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
                ("admin", h, s, "admin", time.time())
            )
            # Also seed demo operator
            h_op, s_op = hash_password("Operator2026!")
            cur.execute(
                "INSERT INTO users (username, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
                ("operator", h_op, s_op, "operator", time.time())
            )

        conn.commit()
        conn.close()

    def _init_postgres(self):
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'viewer',
                created_at DOUBLE PRECISION NOT NULL
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS edge_devices (
                device_id VARCHAR(100) PRIMARY KEY,
                device_name VARCHAR(150) NOT NULL,
                device_token VARCHAR(255) NOT NULL,
                last_heartbeat DOUBLE PRECISION NOT NULL,
                status VARCHAR(50) NOT NULL,
                camera_source VARCHAR(200),
                cpu_percent DOUBLE PRECISION DEFAULT 0.0,
                memory_mb DOUBLE PRECISION DEFAULT 0.0,
                active_pipeline INTEGER DEFAULT 0,
                created_at DOUBLE PRECISION NOT NULL
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS occupancy_telemetry (
                id SERIAL PRIMARY KEY,
                timestamp DOUBLE PRECISION NOT NULL,
                device_id VARCHAR(100) DEFAULT 'dell-edge-01',
                camera_id VARCHAR(100) NOT NULL,
                detected_count INTEGER NOT NULL,
                active_tracks INTEGER NOT NULL,
                tripwire_occupancy INTEGER NOT NULL,
                entries INTEGER NOT NULL,
                exits INTEGER NOT NULL,
                activity_class VARCHAR(50) NOT NULL,
                confidence DOUBLE PRECISION NOT NULL,
                blur_score DOUBLE PRECISION,
                brightness DOUBLE PRECISION,
                is_reliable INTEGER NOT NULL
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id VARCHAR(100) PRIMARY KEY,
                timestamp DOUBLE PRECISION NOT NULL,
                device_id VARCHAR(100) DEFAULT 'dell-edge-01',
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                zone_id VARCHAR(100),
                acknowledged INTEGER DEFAULT 0
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS system_health_logs (
                id SERIAL PRIMARY KEY,
                timestamp DOUBLE PRECISION NOT NULL,
                device_id VARCHAR(100) DEFAULT 'dell-edge-01',
                fps DOUBLE PRECISION NOT NULL,
                latency_ms DOUBLE PRECISION NOT NULL,
                cpu_percent DOUBLE PRECISION NOT NULL,
                memory_mb DOUBLE PRECISION NOT NULL,
                camera_status VARCHAR(100) NOT NULL
            );
            """)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_time ON occupancy_telemetry(timestamp);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp);")

            # Check if admin exists
            cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
            if not cur.fetchone():
                h, s = hash_password("SentinelAdmin2026!")
                cur.execute(
                    "INSERT INTO users (username, password_hash, salt, role, created_at) VALUES (%s, %s, %s, %s, %s)",
                    ("admin", h, s, "admin", time.time())
                )
                h_op, s_op = hash_password("Operator2026!")
                cur.execute(
                    "INSERT INTO users (username, password_hash, salt, role, created_at) VALUES (%s, %s, %s, %s, %s)",
                    ("operator", h_op, s_op, "operator", time.time())
                )

            conn.commit()
            conn.close()
        except Exception as e:
            # Fallback will gracefully occur if DB connection string not yet live
            pass

    # --- Authentication Queries ---
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        q = "SELECT id, username, password_hash, salt, role FROM users WHERE username = %s" if self.is_postgres else "SELECT id, username, password_hash, salt, role FROM users WHERE username = ?"
        cur.execute(q, (username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        user_dict = dict(row)
        if verify_password(password, user_dict["password_hash"], user_dict["salt"]):
            return {
                "id": user_dict["id"],
                "username": user_dict["username"],
                "role": user_dict["role"]
            }
        return None

    # --- Edge Device Management ---
    def register_or_update_device(self, device_id: str, name: str, token: str, camera_source: str = "Hardware Camera") -> Dict[str, Any]:
        now = time.time()
        conn = self._get_connection()
        cur = conn.cursor()
        if self.is_postgres:
            q = """
            INSERT INTO edge_devices (device_id, device_name, device_token, last_heartbeat, status, camera_source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                device_name = EXCLUDED.device_name,
                device_token = EXCLUDED.device_token,
                last_heartbeat = EXCLUDED.last_heartbeat,
                camera_source = EXCLUDED.camera_source;
            """
            cur.execute(q, (device_id, name, token, now, "ONLINE", camera_source, now))
        else:
            q = """
            INSERT INTO edge_devices (device_id, device_name, device_token, last_heartbeat, status, camera_source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (device_id) DO UPDATE SET
                device_name = excluded.device_name,
                device_token = excluded.device_token,
                last_heartbeat = excluded.last_heartbeat,
                camera_source = excluded.camera_source;
            """
            cur.execute(q, (device_id, name, token, now, "ONLINE", camera_source, now))
        conn.commit()
        conn.close()
        return {"device_id": device_id, "status": "registered", "timestamp": now}

    def record_heartbeat(self, device_id: str, cpu_percent: float, memory_mb: float, status: str, camera_source: str, active_pipeline: bool):
        now = time.time()
        conn = self._get_connection()
        cur = conn.cursor()
        q = """
        UPDATE edge_devices 
        SET last_heartbeat = %s, cpu_percent = %s, memory_mb = %s, status = %s, camera_source = %s, active_pipeline = %s
        WHERE device_id = %s
        """ if self.is_postgres else """
        UPDATE edge_devices 
        SET last_heartbeat = ?, cpu_percent = ?, memory_mb = ?, status = ?, camera_source = ?, active_pipeline = ?
        WHERE device_id = ?
        """
        cur.execute(q, (now, cpu_percent, memory_mb, status, camera_source, 1 if active_pipeline else 0, device_id))
        conn.commit()
        conn.close()

    def get_edge_devices(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM edge_devices ORDER BY last_heartbeat DESC")
        rows = cur.fetchall()
        conn.close()
        now = time.time()
        devices = []
        for r in rows:
            d = dict(r)
            # Edge device considered online if heartbeat seen within last 30 seconds
            is_online = (now - d["last_heartbeat"]) < 30.0
            d["is_online"] = is_online
            d["status"] = "ONLINE" if is_online else "OFFLINE"
            d["seconds_since_heartbeat"] = round(now - d["last_heartbeat"], 1)
            devices.append(d)
        return devices

    # --- Telemetry & Ingestion ---
    def record_telemetry(self, camera_id: str, detected_count: int, active_tracks: int, tripwire_occupancy: int,
                         entries: int, exits: int, activity_class: str, confidence: float, blur_score: float,
                         brightness: float, is_reliable: bool, device_id: str = "dell-edge-01", timestamp: Optional[float] = None):
        t_stamp = timestamp or time.time()
        conn = self._get_connection()
        cur = conn.cursor()
        if self.is_postgres:
            q = """
            INSERT INTO occupancy_telemetry 
            (timestamp, device_id, camera_id, detected_count, active_tracks, tripwire_occupancy, entries, exits, activity_class, confidence, blur_score, brightness, is_reliable)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            q = """
            INSERT INTO occupancy_telemetry 
            (timestamp, device_id, camera_id, detected_count, active_tracks, tripwire_occupancy, entries, exits, activity_class, confidence, blur_score, brightness, is_reliable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        cur.execute(q, (t_stamp, device_id, camera_id, detected_count, active_tracks, tripwire_occupancy, entries, exits,
                        activity_class, confidence, blur_score, brightness, 1 if is_reliable else 0))
        conn.commit()
        conn.close()

    def record_alert(self, alert_id: str, alert_type: str, severity: str, title: str, description: str, zone_id: Optional[str], device_id: str = "dell-edge-01"):
        now = time.time()
        conn = self._get_connection()
        cur = conn.cursor()
        if self.is_postgres:
            q = """
            INSERT INTO alerts (id, timestamp, device_id, alert_type, severity, title, description, zone_id, acknowledged)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)
            ON CONFLICT (id) DO NOTHING;
            """
        else:
            q = """
            INSERT OR REPLACE INTO alerts (id, timestamp, device_id, alert_type, severity, title, description, zone_id, acknowledged)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """
        cur.execute(q, (alert_id, now, device_id, alert_type, severity, title, description, zone_id))
        conn.commit()
        conn.close()

    def get_latest_telemetry(self, device_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if device_id:
            q = "SELECT * FROM occupancy_telemetry WHERE device_id = %s ORDER BY timestamp DESC LIMIT 1" if self.is_postgres else "SELECT * FROM occupancy_telemetry WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1"
            cur.execute(q, (device_id,))
        else:
            cur.execute("SELECT * FROM occupancy_telemetry ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_recent_telemetry(self, limit: int = 50, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if device_id:
            q = "SELECT * FROM occupancy_telemetry WHERE device_id = %s ORDER BY timestamp DESC LIMIT %s" if self.is_postgres else "SELECT * FROM occupancy_telemetry WHERE device_id = ? ORDER BY timestamp DESC LIMIT ?"
            cur.execute(q, (device_id, limit))
        else:
            q = "SELECT * FROM occupancy_telemetry ORDER BY timestamp DESC LIMIT %s" if self.is_postgres else "SELECT * FROM occupancy_telemetry ORDER BY timestamp DESC LIMIT ?"
            cur.execute(q, (limit,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    def get_aggregated_hourly(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if self.is_postgres:
            q = """
            SELECT 
                to_char(to_timestamp(timestamp), 'HH24:00') as hour,
                AVG(detected_count) as avg_count,
                MAX(detected_count) as max_count,
                MAX(entries) as total_entries,
                MAX(exits) as total_exits
            FROM occupancy_telemetry
            GROUP BY hour
            ORDER BY hour ASC
            """
        else:
            q = """
            SELECT 
                strftime('%H:00', datetime(timestamp, 'unixepoch', 'localtime')) as hour,
                AVG(detected_count) as avg_count,
                MAX(detected_count) as max_count,
                MAX(entries) as total_entries,
                MAX(exits) as total_exits
            FROM occupancy_telemetry
            GROUP BY hour
            ORDER BY hour ASC
            """
        cur.execute(q)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

# Backward compatible helper
def init_db(db_path: str = DB_PATH):
    DatabaseManager(f"sqlite:///{db_path}")
