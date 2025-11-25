#!/usr/bin/env python3
"""
Netlify Function: Set Initial Cash Balance
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Set initial cash balance"""
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        balance = float(body['balance'])
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current positions value
        cursor.execute('SELECT SUM(quantity * entry_price) as total FROM positions WHERE is_open = TRUE')
        total_pos = cursor.fetchone()['total'] or 0
        portfolio_value = balance + total_pos
        
        # Record performance
        cursor.execute('''
            INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (datetime.now().date(), 'manual', balance, portfolio_value, 0, 0))
        
        conn.commit()
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
                'message': f'Balance set to ${balance:.2f}',
                'balance': balance,
                'portfolio_value': portfolio_value
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
            'body': json.dumps({'success': False, 'error': str(e)})
        }

