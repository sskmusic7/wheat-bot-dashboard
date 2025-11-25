#!/usr/bin/env python3
"""
Netlify Function: Get Portfolio Overview
"""

import json
import sys
import os

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_shared'))

from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Get portfolio overview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get open positions
        cursor.execute('''
            SELECT * FROM positions 
            WHERE is_open = TRUE 
            ORDER BY entry_date DESC
        ''')
        positions = [dict(row) for row in cursor.fetchall()]
        
        # Calculate portfolio value
        total_position_value = sum(p['quantity'] * p['entry_price'] for p in positions)
        
        # Get recent performance
        cursor.execute('''
            SELECT * FROM performance 
            ORDER BY date DESC 
            LIMIT 1
        ''')
        perf = cursor.fetchone()
        
        if perf:
            cash_balance = float(perf['cash_balance'])
            portfolio_value = float(perf['portfolio_value'])
        else:
            cash_balance = 0
            portfolio_value = 0
        
        # Get trade stats (30 days)
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl_pct) as avg_pnl_pct,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades
            FROM trades
            WHERE exit_date >= NOW() - INTERVAL '30 days'
        ''')
        stats_30d = dict(cursor.fetchone() or {})
        
        # Get trade stats (7 days)
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl_pct) as avg_pnl_pct,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades
            FROM trades
            WHERE exit_date >= NOW() - INTERVAL '7 days'
        ''')
        stats_7d = dict(cursor.fetchone() or {})
        
        # Ensure all values are not None
        stats_30d = {k: (float(v) if v is not None else 0) for k, v in stats_30d.items()}
        stats_7d = {k: (float(v) if v is not None else 0) for k, v in stats_7d.items()}
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'data': {
                    'portfolio_value': float(portfolio_value),
                    'cash_balance': float(cash_balance),
                    'position_value': float(total_position_value),
                    'total_positions': len(positions),
                    'stats_30d': stats_30d,
                    'stats_7d': stats_7d
                }
            })
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

