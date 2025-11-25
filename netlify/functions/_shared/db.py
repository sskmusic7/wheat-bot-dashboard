#!/usr/bin/env python3
"""
Neon Database Adapter for Netlify Functions
Connects to Neon PostgreSQL database
"""

import os
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    # Fallback for local testing
    psycopg2 = None
    RealDictCursor = None

from typing import Dict, List, Optional
from datetime import datetime
import json

def get_db_connection():
    """Get database connection from environment variable"""
    connection_string = os.environ.get('NETLIFY_DATABASE_URL') or os.environ.get('NEON_DATABASE_URL')
    
    if not connection_string:
        raise ValueError('NETLIFY_DATABASE_URL or NEON_DATABASE_URL environment variable not set')
    
    return psycopg2.connect(connection_string)

def ensure_tables():
    """Ensure all tables exist in Neon database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Positions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            entry_date TIMESTAMP NOT NULL,
            source TEXT NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            notes TEXT,
            is_open BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            entry_date TIMESTAMP NOT NULL,
            exit_date TIMESTAMP NOT NULL,
            pnl REAL NOT NULL,
            pnl_pct REAL NOT NULL,
            source TEXT NOT NULL,
            strategy TEXT,
            exit_reason TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            signal TEXT NOT NULL,
            predicted_change REAL NOT NULL,
            current_price REAL NOT NULL,
            predicted_price REAL NOT NULL,
            factors JSONB NOT NULL,
            justification TEXT,
            confidence REAL,
            was_executed BOOLEAN DEFAULT FALSE,
            actual_change REAL,
            signal_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Performance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            source TEXT NOT NULL,
            cash_balance REAL NOT NULL,
            portfolio_value REAL NOT NULL,
            total_pnl REAL NOT NULL,
            daily_return REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # News alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_alerts (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            author TEXT,
            importance TEXT DEFAULT 'normal',
            published_at TIMESTAMP,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            notified BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Initialize tables on import
try:
    ensure_tables()
except Exception as e:
    print(f"Warning: Could not initialize tables: {e}")

