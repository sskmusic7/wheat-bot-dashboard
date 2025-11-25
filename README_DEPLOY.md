# Netlify Dashboard Deployment Guide

This guide explains how to deploy the Trading Bot Dashboard to Netlify using Neon PostgreSQL database.

## Prerequisites

1. **Netlify Account** - Sign up at https://netlify.com
2. **Neon Database** - You should already have this set up for the signal pager
3. **Netlify CLI** - Install with `npm install -g netlify-cli`

## Step 1: Set Up Neon Database Tables

The dashboard needs the same database tables. Run this SQL in your Neon console:

```sql
-- Positions table
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
);

-- Trades table
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
);

-- Signals table
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
);

-- Performance table
CREATE TABLE IF NOT EXISTS performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    source TEXT NOT NULL,
    cash_balance REAL NOT NULL,
    portfolio_value REAL NOT NULL,
    total_pnl REAL NOT NULL,
    daily_return REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News alerts table
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
);
```

## Step 2: Copy Dashboard Files

1. Copy `Trading Bot/templates/dashboard.html` to `dashboard_netlify/public/index.html`
2. Update all API calls in the HTML from `/api/...` to `/.netlify/functions/...`

For example:
- `/api/overview` → `/.netlify/functions/overview`
- `/api/positions` → `/.netlify/functions/positions`
- `/api/trades` → `/.netlify/functions/trades`
- `/api/signals` → `/.netlify/functions/signals`

## Step 3: Create Netlify Site

```bash
cd dashboard_netlify
netlify init
```

Choose:
- "Create & configure a new site"
- Select your team
- Site name: `wheat-bot-dashboard` (or your choice)

## Step 4: Set Environment Variables

Set your Neon database URL:

```bash
netlify env:set NETLIFY_DATABASE_URL "postgresql://user:password@host/database"
```

Or set it in the Netlify UI:
1. Go to Site settings → Environment variables
2. Add `NETLIFY_DATABASE_URL` with your Neon connection string

## Step 5: Deploy

```bash
netlify deploy --prod
```

Or use the Netlify UI:
1. Connect your GitHub repo
2. Set build directory to `dashboard_netlify`
3. Deploy automatically on push

## Step 6: Complete Netlify Functions

You'll need to create Netlify Functions for all API endpoints:

- `overview.py` ✅ (created)
- `positions.py` ✅ (created)
- `trades.py` (needs to be created)
- `signals.py` (needs to be created)
- `close_position.py` (needs to be created)
- `set_balance.py` (needs to be created)
- `run_wheat_bot.py` (needs to be created)
- `notes.py` (needs to be created)
- `news_alerts.py` (needs to be created)

## Migration from Local SQLite

To migrate your existing data from SQLite to Neon:

1. Export data from SQLite:
```python
# Run this in Trading Bot directory
python export_to_json.py
```

2. Import to Neon:
```python
# Run this with Neon connection
python import_from_json.py
```

## Notes

- The dashboard will be publicly accessible (no authentication)
- All data is stored in Neon PostgreSQL (cloud database)
- Netlify Functions have a 10-second timeout (for longer operations, use background jobs)
- The dashboard is read-only for most operations (buy/sell requires additional setup)

## Troubleshooting

**Functions not working?**
- Check Netlify Function logs: `netlify functions:list`
- Verify `NETLIFY_DATABASE_URL` is set
- Check Neon database connection

**Database connection errors?**
- Verify Neon connection string format
- Check Neon database is running
- Ensure tables are created

**CORS errors?**
- Functions should include `Access-Control-Allow-Origin: *` headers (already added)

