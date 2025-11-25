#!/usr/bin/env python3
"""
Netlify Function: Notes Management
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../_shared'))
from db import get_db_connection
from psycopg2.extras import RealDictCursor

def handler(event, context):
    """Handle notes API"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if method == 'GET':
            # Get all notes
            query_params = event.get('queryStringParameters') or {}
            category = query_params.get('category')
            
            query = 'SELECT * FROM notes WHERE 1=1'
            params = []
            
            if category:
                query += ' AND category = %s'
                params.append(category)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            notes = [dict(row) for row in cursor.fetchall()]
            
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
                    'data': notes
                }, default=str)
            }
        
        elif method == 'POST':
            # Add note
            body = json.loads(event.get('body', '{}'))
            
            cursor.execute('''
                INSERT INTO notes (title, content, category)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', (
                body['title'],
                body['content'],
                body.get('category', 'general')
            ))
            
            note_id = cursor.fetchone()['id']
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
                    'note_id': note_id,
                    'message': 'Note added successfully'
                })
            }
        
        elif method == 'DELETE':
            # Delete note
            query_params = event.get('queryStringParameters') or {}
            note_id = query_params.get('id')
            
            if not note_id:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Note ID required'})
                }
            
            cursor.execute('DELETE FROM notes WHERE id = %s', (note_id,))
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
                    'message': 'Note deleted successfully'
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

