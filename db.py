"""
db.py — SQLite database layer for Retina AI Portal
"""
import sqlite3, bcrypt, os
from datetime import datetime
from pathlib import Path

DB_PATH = "retina_ai.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        email       TEXT    UNIQUE NOT NULL,
        password    TEXT    NOT NULL,
        phone       TEXT,
        city        TEXT,
        state       TEXT,
        address     TEXT,
        created_at  TEXT    DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS clinics (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        clinic_name     TEXT NOT NULL,
        doctor_name     TEXT NOT NULL,
        email           TEXT UNIQUE NOT NULL,
        password        TEXT NOT NULL,
        phone           TEXT NOT NULL,
        city            TEXT NOT NULL,
        state           TEXT NOT NULL,
        address         TEXT NOT NULL,
        specialization  TEXT DEFAULT 'Ophthalmology',
        reg_number      TEXT,
        approved        INTEGER DEFAULT 0,
        created_at      TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS detections (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        filename     TEXT,
        result       TEXT,
        disease_prob REAL,
        normal_prob  REAL,
        confidence   REAL,
        risk_level   TEXT,
        timestamp    TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        clinic_id    INTEGER NOT NULL,
        detection_id INTEGER,
        status       TEXT DEFAULT 'pending',
        notes        TEXT,
        timestamp    TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id)   REFERENCES users(id),
        FOREIGN KEY (clinic_id) REFERENCES clinics(id)
    );
    """)
    conn.commit()
    conn.close()

# ── Password helpers ───────────────────────────────────────────────────
def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_pw(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── User CRUD ─────────────────────────────────────────────────────────
def register_user(name, email, password, phone, city, state, address):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name,email,password,phone,city,state,address) VALUES (?,?,?,?,?,?,?)",
            (name, email, hash_pw(password), phone, city, state, address)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()

def login_user(email, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if row and check_pw(password, row["password"]):
        return dict(row), None
    return None, "Invalid email or password."

def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT id,name,email,phone,city,state,created_at FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(uid):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()

def update_user_location(uid, city, state, address):
    conn = get_conn()
    conn.execute("UPDATE users SET city=?, state=?, address=? WHERE id=?",
                 (city, state, address, uid))
    conn.commit()
    conn.close()

# ── Clinic CRUD ───────────────────────────────────────────────────────
def register_clinic(clinic_name, doctor_name, email, password,
                    phone, city, state, address, specialization, reg_number):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO clinics
               (clinic_name,doctor_name,email,password,phone,city,state,
                address,specialization,reg_number)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (clinic_name, doctor_name, email, hash_pw(password),
             phone, city, state, address, specialization, reg_number)
        )
        conn.commit()
        return True, "Clinic registration submitted! Awaiting admin approval."
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()

def login_clinic(email, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM clinics WHERE email=?", (email,)).fetchone()
    conn.close()
    if row and check_pw(password, row["password"]):
        if not row["approved"]:
            return None, "Your clinic is pending admin approval."
        return dict(row), None
    return None, "Invalid email or password."

def get_all_clinics(approved_only=False):
    conn = get_conn()
    q = "SELECT * FROM clinics"
    if approved_only:
        q += " WHERE approved=1"
    q += " ORDER BY id DESC"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_clinic(cid):
    conn = get_conn()
    conn.execute("UPDATE clinics SET approved=1 WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def reject_clinic(cid):
    conn = get_conn()
    conn.execute("DELETE FROM clinics WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def get_nearby_clinics(city, state):
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM clinics WHERE approved=1 AND (
           LOWER(city)=LOWER(?) OR LOWER(state)=LOWER(?))
           ORDER BY LOWER(city)=LOWER(?) DESC""",
        (city, state, city)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Detection CRUD ────────────────────────────────────────────────────
def save_detection(user_id, filename, result, disease_prob,
                   normal_prob, confidence, risk_level):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO detections
           (user_id,filename,result,disease_prob,normal_prob,confidence,risk_level)
           VALUES (?,?,?,?,?,?,?)""",
        (user_id, filename, result, disease_prob, normal_prob, confidence, risk_level)
    )
    conn.commit()
    det_id = cur.lastrowid
    conn.close()
    return det_id

def get_user_detections(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM detections WHERE user_id=? ORDER BY timestamp DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Booking CRUD ──────────────────────────────────────────────────────
def create_booking(user_id, clinic_id, detection_id, notes=""):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO bookings (user_id,clinic_id,detection_id,notes) VALUES (?,?,?,?)",
            (user_id, clinic_id, detection_id, notes)
        )
        conn.commit()
        return True, "Appointment booked successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_clinic_bookings(clinic_id):
    conn = get_conn()
    rows = conn.execute(
        """SELECT b.*, u.name as user_name, u.phone as user_phone,
                  u.city as user_city, d.result, d.risk_level, d.disease_prob
           FROM bookings b
           JOIN users u ON b.user_id=u.id
           LEFT JOIN detections d ON b.detection_id=d.id
           WHERE b.clinic_id=?
           ORDER BY b.timestamp DESC""",
        (clinic_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_bookings(user_id):
    conn = get_conn()
    rows = conn.execute(
        """SELECT b.*, c.clinic_name, c.doctor_name, c.phone as clinic_phone,
                  c.city as clinic_city, c.address as clinic_address
           FROM bookings b
           JOIN clinics c ON b.clinic_id=c.id
           WHERE b.user_id=?
           ORDER BY b.timestamp DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_booking_status(bid, status):
    conn = get_conn()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, bid))
    conn.commit()
    conn.close()

# ── Admin stats ────────────────────────────────────────────────────────
def get_stats():
    conn = get_conn()
    stats = {
        "total_users":     conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_clinics":   conn.execute("SELECT COUNT(*) FROM clinics WHERE approved=1").fetchone()[0],
        "pending_clinics": conn.execute("SELECT COUNT(*) FROM clinics WHERE approved=0").fetchone()[0],
        "total_detections":conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0],
        "total_bookings":  conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
        "high_risk":       conn.execute("SELECT COUNT(*) FROM detections WHERE risk_level='HIGH'").fetchone()[0],
    }
    conn.close()
    return stats

# Admin credentials (hardcoded)
ADMIN_EMAIL    = "admin@retinaai.com"
ADMIN_PASSWORD = "Admin@123"

def login_admin(email, password):
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return {"name": "Administrator", "email": email, "role": "admin"}
    return None
