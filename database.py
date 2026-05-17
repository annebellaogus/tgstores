# ============================================
# DATABASE MODELS & OPERATIONS
# ============================================
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
import os

DB_PATH = "session_store.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_date TEXT,
            total_orders INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            is_banned INTEGER DEFAULT 0
        )
    ''')
    
    # Stock table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            phone_number TEXT,
            session_string TEXT,
            json_data TEXT,
            is_sold INTEGER DEFAULT 0,
            added_date TEXT,
            age_months INTEGER DEFAULT 0,
            country TEXT DEFAULT 'Unknown'
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            user_id INTEGER,
            category TEXT,
            item_id INTEGER,
            amount REAL,
            currency TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            paid_at TEXT,
            delivered_at TEXT,
            phone_number TEXT,
            session_string TEXT,
            json_data TEXT
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            user_id INTEGER,
            amount REAL,
            currency TEXT,
            method TEXT,
            screenshot_path TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            verified_by INTEGER,
            verified_at TEXT
        )
    ''')
    
    # Stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total_users INTEGER DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            total_revenue REAL DEFAULT 0,
            updated_at TEXT
        )
    ''')
    
    # Insert default stats if not exists
    cursor.execute("INSERT OR IGNORE INTO stats (id, updated_at) VALUES (1, ?)", 
                   (datetime.now().isoformat(),))
    
    conn.commit()
    conn.close()

# ============== USER OPERATIONS ==============

def add_user(user_id: int, username: str, first_name: str, last_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY joined_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def ban_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ============== STOCK OPERATIONS ==============

def add_stock(category: str, phone_number: str, session_string: str, 
              json_data: str = "", age_months: int = 0, country: str = "Unknown"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stock (category, phone_number, session_string, json_data, added_date, age_months, country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, phone_number, session_string, json_data, datetime.now().isoformat(), age_months, country))
    conn.commit()
    conn.close()

def get_available_stock(category: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM stock WHERE category = ? AND is_sold = 0
    ''', (category,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stock_count(category: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT COUNT(*) FROM stock WHERE category = ? AND is_sold = 0", (category,))
    else:
        cursor.execute("SELECT COUNT(*) FROM stock WHERE is_sold = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_stock() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock ORDER BY added_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def mark_stock_sold(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE stock SET is_sold = 1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def delete_stock(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stock WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# ============== ORDER OPERATIONS ==============

def create_order(user_id: int, category: str, amount: float, currency: str, 
                 payment_method: str) -> str:
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (order_id, user_id, category, amount, currency, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, user_id, category, amount, currency, payment_method, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return order_id

def get_order(order_id: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_orders(user_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_orders() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_order_status(order_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    if status == "paid":
        cursor.execute("UPDATE orders SET status = ?, paid_at = ? WHERE order_id = ?", 
                      (status, datetime.now().isoformat(), order_id))
    elif status == "delivered":
        cursor.execute("UPDATE orders SET status = ?, delivered_at = ? WHERE order_id = ?", 
                      (status, datetime.now().isoformat(), order_id))
    else:
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()

def deliver_order(order_id: str, item_id: int, phone: str, session: str, json_data: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders SET item_id = ?, phone_number = ?, session_string = ?, json_data = ?, 
        status = 'delivered', delivered_at = ? WHERE order_id = ?
    ''', (item_id, phone, session, json_data, datetime.now().isoformat(), order_id))
    conn.commit()
    conn.close()
    mark_stock_sold(item_id)

# ============== PAYMENT OPERATIONS ==============

def add_payment(order_id: str, user_id: int, amount: float, currency: str, 
                method: str, screenshot_path: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (order_id, user_id, amount, currency, method, screenshot_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, user_id, amount, currency, method, screenshot_path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_pending_payments() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def verify_payment(payment_id: int, admin_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE payments SET status = 'verified', verified_by = ?, verified_at = ?
        WHERE id = ?
    ''', (admin_id, datetime.now().isoformat(), payment_id))
    conn.commit()
    conn.close()

# ============== STATS OPERATIONS ==============

def get_stats() -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stats WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered'")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM orders WHERE status = 'delivered'")
    total_revenue = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        UPDATE stats SET total_users = ?, total_orders = ?, total_revenue = ?, updated_at = ?
        WHERE id = 1
    ''', (total_users, total_orders, total_revenue, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()
