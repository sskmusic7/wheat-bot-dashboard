#!/usr/bin/env python3
"""
Netlify Function: Close Position
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Close a position"""
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        position_id = int(body['position_id'])
        exit_price = float(body['exit_price'])
        exit_reason = body.get('exit_reason', 'manual')
        notes = body.get('notes')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get position
        cursor.execute('SELECT * FROM positions WHERE id = %s', (position_id,))
        position = cursor.fetchone()
        
        if not position:
            cursor.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Position not found'})
            }
        
        position = dict(position)
        
        if not position['is_open']:
            cursor.close()
            conn.close()
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Position already closed'})
            }
        
        # Calculate P&L
        pnl = (exit_price - position['entry_price']) * position['quantity']
        pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        
        # Close position
        cursor.execute('''
            UPDATE positions SET is_open = FALSE, updated_at = %s
            WHERE id = %s
        ''', (datetime.now(), position_id))
        
        # Record trade
        cursor.execute('''
            INSERT INTO trades (symbol, quantity, entry_price, exit_price,
                              entry_date, exit_date, pnl, pnl_pct,
                              source, exit_reason, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            position['symbol'], position['quantity'], position['entry_price'],
            exit_price, position['entry_date'], datetime.now(),
            pnl, pnl_pct, position['source'], exit_reason, notes
        ))
        
        # Update cash balance
        proceeds = position['quantity'] * exit_price
        cursor.execute('''
            SELECT cash_balance FROM performance 
            ORDER BY date DESC LIMIT 1
        ''')
        perf = cursor.fetchone()
        current_cash = float(perf['cash_balance']) if perf else 0
        new_cash = current_cash + proceeds
        
        # Get remaining positions
        cursor.execute('SELECT SUM(quantity * entry_price) as total FROM positions WHERE is_open = TRUE')
        total_pos = cursor.fetchone()['total'] or 0
        new_portfolio = new_cash + total_pos
        
        # Get total P&L
        cursor.execute('SELECT SUM(pnl) as total FROM trades')
        total_pnl = cursor.fetchone()['total'] or 0
        
        cursor.execute('''
            INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (datetime.now().date(), 'manual', new_cash, new_portfolio, total_pnl, 0))
        
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
                'pnl': float(pnl),
                'pnl_pct': float(pnl_pct),
                'proceeds': float(proceeds),
                'new_cash_balance': float(new_cash),
                'message': f'Position closed. P&L: ${pnl:.2f} ({pnl_pct:+.2f}%). Cash: ${new_cash:.2f}'
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

