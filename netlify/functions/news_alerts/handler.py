#!/usr/bin/env python3
"""
Netlify Function: News Alerts Management
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Handle news alerts API"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if method == 'GET':
            # Get news alerts
            query_params = event.get('queryStringParameters') or {}
            unread_only = query_params.get('unread_only') == 'true'
            limit = int(query_params.get('limit', 50))
            
            query = 'SELECT * FROM news_alerts WHERE 1=1'
            params = []
            
            if unread_only:
                query += ' AND is_read = FALSE'
            
            query += ' ORDER BY received_at DESC LIMIT %s'
            params.append(limit)
            
            cursor.execute(query, params)
            alerts = [dict(row) for row in cursor.fetchall()]
            
            # Get unread count
            cursor.execute('SELECT COUNT(*) as count FROM news_alerts WHERE is_read = FALSE')
            unread_count = cursor.fetchone()['count']
            
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
                    'data': alerts,
                    'unread_count': unread_count
                }, default=str)
            }
        
        elif method == 'POST':
            # Mark as read
            body = json.loads(event.get('body', '{}'))
            alert_id = body.get('alert_id')
            
            if alert_id:
                cursor.execute('UPDATE news_alerts SET is_read = TRUE WHERE id = %s', (alert_id,))
            else:
                # Mark all as read
                cursor.execute('UPDATE news_alerts SET is_read = TRUE WHERE is_read = FALSE')
            
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
                    'message': 'Alerts updated'
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

