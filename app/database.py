"""
Database management module for IMM.
Handles SQLite database connection, schema initialization, and query execution.
"""

import os
import sqlite3
from typing import Optional, Any, List, Tuple


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "app.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a SQLite database connection with row factory configured."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: reels (stores target and processed reels)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reel_id TEXT UNIQUE NOT NULL,
            shortcode TEXT NOT NULL,
            author_username TEXT NOT NULL,
            caption TEXT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        );
    """)

    # Table: comments (stores generated and submitted comments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reel_id TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'approved', 'submitted', 'failed', 'rejected')) DEFAULT 'pending',
            sent_at TIMESTAMP,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reel_id) REFERENCES reels (reel_id)
        );
    """)

    # Table: activity_logs (stores system activity history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table: list_entries (stores blacklist and whitelist entries)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS list_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_value TEXT UNIQUE NOT NULL,
            list_type TEXT CHECK(list_type IN ('blacklist', 'whitelist')) NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def execute_query(query: str, params: Tuple[Any, ...] = ()) -> Optional[int]:
    """Executes an INSERT, UPDATE, or DELETE query with parameters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def fetch_all(query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
    """Executes a SELECT query and returns all matching rows."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_one(query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
    """Executes a SELECT query and returns the first matching row."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return row
  
