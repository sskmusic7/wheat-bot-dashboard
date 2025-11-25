#!/usr/bin/env python3
"""
Netlify Function: Get Watchlist Quotes
"""

import json
import sys
import os
import urllib.request

def handler(event, context):
    """Get quotes for watchlist symbols"""
    try:
        # Default wheat-related symbols
        symbols = ['WEAT', 'SOYB', 'CORN', 'DBA', 'ADM', 'BG']
        
        query_params = event.get('queryStringParameters') or {}
        if query_params.get('symbols'):
            symbols = query_params['symbols'].split(',')
        
        quotes = []
        
        for symbol in symbols:
            try:
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    
                    if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        quotes.append({
                            'symbol': symbol,
                            'price': meta.get('regularMarketPrice'),
                            'change': meta.get('regularMarketChange'),
                            'changePercent': meta.get('regularMarketChangePercent'),
                            'volume': meta.get('regularMarketVolume')
                        })
            except:
                # Skip symbols that fail
                continue
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'data': quotes
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

