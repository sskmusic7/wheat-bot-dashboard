#!/usr/bin/env python3
"""
Netlify Function: Get/Add/Close Positions
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Handle positions API"""
    method = event.get('httpMethod', 'GET')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if method == 'GET':
            # Get all open positions
            cursor.execute('''
                SELECT * FROM positions 
                WHERE is_open = TRUE 
                ORDER BY entry_date DESC
            ''')
            positions = [dict(row) for row in cursor.fetchall()]
            
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
                    'data': positions
                }, default=str)
            }
        
        elif method == 'POST':
            # Add new position
            body = json.loads(event.get('body', '{}'))
            
            cursor.execute('''
                INSERT INTO positions (symbol, quantity, entry_price, entry_date, source,
                                     stop_loss, take_profit, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                body['symbol'],
                float(body['quantity']),
                float(body['entry_price']),
                datetime.now(),
                body.get('source', 'manual'),
                body.get('stop_loss'),
                body.get('take_profit'),
                body.get('notes')
            ))
            
            position_id = cursor.fetchone()['id']
            
            # Update cash balance
            cost = float(body['quantity']) * float(body['entry_price'])
            cursor.execute('''
                SELECT cash_balance FROM performance 
                ORDER BY date DESC LIMIT 1
            ''')
            perf = cursor.fetchone()
            current_cash = float(perf['cash_balance']) if perf else 0
            
            if cost > current_cash:
                conn.rollback()
                cursor.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': f'Insufficient funds. Need ${cost:.2f}, have ${current_cash:.2f}'
                    })
                }
            
            new_cash = current_cash - cost
            cursor.execute('''
                SELECT SUM(quantity * entry_price) as total FROM positions WHERE is_open = TRUE
            ''')
            total_pos = cursor.fetchone()['total'] or 0
            new_portfolio = new_cash + total_pos
            
            cursor.execute('''
                INSERT INTO performance (date, source, cash_balance, portfolio_value, total_pnl, daily_return)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (datetime.now().date(), 'manual', new_cash, new_portfolio, 0, 0))
            
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
                    'position_id': position_id,
                    'message': f'Position {body["symbol"]} added. Cost: ${cost:.2f}, Remaining: ${new_cash:.2f}'
                })
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Method not allowed'})
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

