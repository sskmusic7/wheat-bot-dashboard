#!/usr/bin/env python3
"""
Netlify Function: Get Recent Signals
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Get recent signals"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        symbol = query_params.get('symbol')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM signals WHERE 1=1'
        params = []
        
        if symbol:
            query += ' AND symbol = %s'
            params.append(symbol)
        
        query += ' ORDER BY signal_date DESC LIMIT %s'
        params.append(limit)
        
        cursor.execute(query, params)
        signals = [dict(row) for row in cursor.fetchall()]
        
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
                'data': signals
            }, default=str)
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

