# Quick Start: Deploy Dashboard to Netlify

## ✅ What's Ready

- ✅ Dashboard HTML migrated to use Netlify Functions
- ✅ Database adapter for Neon PostgreSQL
- ✅ Overview and Positions API functions created
- ✅ Netlify configuration files

## 🚀 Quick Deploy Steps

### 1. Set Up Database Tables

Run the SQL from `README_DEPLOY.md` in your Neon console to create all tables.

### 2. Set Environment Variable

```bash
cd dashboard_netlify
netlify env:set NETLIFY_DATABASE_URL "your-neon-connection-string"
```

### 3. Deploy

```bash
netlify init
netlify deploy --prod
```

## ⚠️ What Still Needs to Be Done

You need to create Netlify Functions for these endpoints:

- `trades.py` - Get trade history
- `signals.py` - Get wheat bot signals  
- `close_position.py` - Close a position
- `set_balance.py` - Set initial cash balance
- `run_wheat_bot.py` - Trigger wheat bot (optional)
- `notes.py` - Notes management
- `news_alerts.py` - News alerts
- `quote.py` - Stock quotes
- `watchlist.py` - Watchlist

## 📝 Example Function Template

```python
#!/usr/bin/env python3
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Your logic here
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': True, 'data': []})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'error': str(e)})
        }
```

## 🔗 Your Dashboard URL

After deployment, your dashboard will be at:
`https://your-site-name.netlify.app`

## 💡 Tips

- All functions need `Access-Control-Allow-Origin: *` for CORS
- Use `RealDictCursor` to get dict results from PostgreSQL
- Functions have 10-second timeout limit
- Check Netlify Function logs for debugging

