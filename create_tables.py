#!/usr/bin/env python3
"""
Create database tables in Neon PostgreSQL
Run this after setting NETLIFY_DATABASE_URL environment variable
"""

import os
import sys

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)

def create_tables():
    connection_string = os.environ.get('NETLIFY_DATABASE_URL') or os.environ.get('NEON_DATABASE_URL')
    
    if not connection_string:
        print("❌ NETLIFY_DATABASE_URL or NEON_DATABASE_URL not set")
        print("   Set it as an environment variable:")
        print("   export NETLIFY_DATABASE_URL='postgresql://user:password@host/database'")
        print("   Or get it from Netlify: netlify env:get NETLIFY_DATABASE_URL")
        return False
    
    try:
        print("🔌 Connecting to Neon database...")
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        print("🔧 Creating database tables...")
        
        # Positions table
        print("  - Creating positions table...")
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
        print("  - Creating trades table...")
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
        print("  - Creating signals table...")
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
        print("  - Creating performance table...")
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
        print("  - Creating notes table...")
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
        print("  - Creating news_alerts table...")
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
        
        print("✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_tables()
    if success:
        print("\n🎉 Database setup complete!")
        print("   Your dashboard is ready to use!")
    else:
        print("\n⚠️  Database setup incomplete.")
        print("   Please check your connection string and try again.")

