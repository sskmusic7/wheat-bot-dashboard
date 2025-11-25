#!/bin/bash
# Complete setup script for Netlify dashboard deployment

set -e

echo "🚀 Completing Netlify Dashboard Setup"
echo "========================================"
echo ""

# Check if Netlify is linked
if ! netlify status &>/dev/null; then
    echo "❌ Not linked to Netlify. Run: netlify link"
    exit 1
fi

echo "✅ Netlify site: wheat-bot-dashboard"
echo "✅ GitHub repo: https://github.com/sskmusic7/wheat-bot-dashboard"
echo ""

# Check for Neon database URL
if [ -z "$NEON_DATABASE_URL" ]; then
    echo "📋 Please provide your Neon database connection string"
    echo "   Format: postgresql://user:password@host/database"
    echo ""
    read -p "Enter Neon Database URL (or press Enter to skip): " NEON_URL
    
    if [ -n "$NEON_URL" ]; then
        echo ""
        echo "🔧 Setting environment variable..."
        netlify env:set NETLIFY_DATABASE_URL "$NEON_URL"
        echo "✅ Environment variable set!"
    else
        echo "⚠️  Skipping environment variable. Set it manually in Netlify dashboard:"
        echo "   Site settings → Environment variables → Add: NETLIFY_DATABASE_URL"
    fi
else
    echo "🔧 Setting environment variable from NEON_DATABASE_URL..."
    netlify env:set NETLIFY_DATABASE_URL "$NEON_DATABASE_URL"
    echo "✅ Environment variable set!"
fi

echo ""
echo "📊 Next: Create database tables in Neon"
echo "   Run the SQL from README_DEPLOY.md in your Neon console"
echo "   Or use the create_tables.py script"
echo ""

# Create database tables script
cat > create_tables.py << 'EOF'
#!/usr/bin/env python3
"""Create database tables in Neon PostgreSQL"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def create_tables():
    connection_string = os.environ.get('NETLIFY_DATABASE_URL') or os.environ.get('NEON_DATABASE_URL')
    
    if not connection_string:
        print("❌ NETLIFY_DATABASE_URL or NEON_DATABASE_URL not set")
        print("   Set it as an environment variable or in Netlify dashboard")
        return
    
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        print("🔧 Creating database tables...")
        
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
        
        print("✅ All tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_tables()
EOF

chmod +x create_tables.py
echo "✅ Created create_tables.py script"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   ✅ GitHub repo: https://github.com/sskmusic7/wheat-bot-dashboard"
echo "   ✅ Netlify site: https://wheat-bot-dashboard.netlify.app"
echo "   ✅ Site linked to Netlify"
echo ""
echo "📝 Remaining steps:"
echo "   1. Set NETLIFY_DATABASE_URL in Netlify (if not set above)"
echo "   2. Create database tables (run create_tables.py or SQL in Neon console)"
echo "   3. Connect GitHub repo in Netlify UI:"
echo "      - Go to https://app.netlify.com/projects/wheat-bot-dashboard"
echo "      - Site settings → Build & deploy → Continuous Deployment"
echo "      - Link to GitHub → Select wheat-bot-dashboard repo"
echo "   4. Deploy!"
echo ""
echo "🔗 Your dashboard will be at: https://wheat-bot-dashboard.netlify.app"

