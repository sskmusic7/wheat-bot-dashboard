#!/usr/bin/env python3
"""
Netlify Function: Get Stock Quote
"""

import json
import sys
import os
import urllib.request
import urllib.parse

def handler(event, context):
    """Get stock quote from Yahoo Finance"""
    try:
        # Extract symbol from path: /.netlify/functions/quote/AAPL
        path = event.get('path', '')
        symbol = path.split('/')[-1] if path else None
        
        if not symbol:
            query_params = event.get('queryStringParameters') or {}
            symbol = query_params.get('symbol')
        
        if not symbol:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Symbol required'})
            }
        
        # Use Yahoo Finance API (free, no key needed)
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    quote = {
                        'symbol': symbol,
                        'price': meta.get('regularMarketPrice'),
                        'change': meta.get('regularMarketChange'),
                        'changePercent': meta.get('regularMarketChangePercent'),
                        'volume': meta.get('regularMarketVolume'),
                        'marketCap': meta.get('marketCap'),
                        'currency': meta.get('currency', 'USD')
                    }
                    
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'success': True,
                            'data': quote
                        })
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Symbol not found'})
                    }
        except urllib.error.HTTPError as e:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Symbol not found: {symbol}'})
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

