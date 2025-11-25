#!/usr/bin/env python3
"""
Script to migrate dashboard.html to use Netlify Functions
Updates all /api/... calls to /.netlify/functions/...
"""

import os
import re

# Paths
SOURCE_DASHBOARD = "../Trading Bot/templates/dashboard.html"
TARGET_DASHBOARD = "public/index.html"

def migrate_api_calls(content):
    """Replace Flask API routes with Netlify Functions"""
    
    # Map Flask routes to Netlify Functions
    route_map = {
        '/api/overview': '/.netlify/functions/overview',
        '/api/positions': '/.netlify/functions/positions',
        '/api/trades': '/.netlify/functions/trades',
        '/api/signals': '/.netlify/functions/signals',
        '/api/close_position': '/.netlify/functions/close_position',
        '/api/set_balance': '/.netlify/functions/set_balance',
        '/api/run_wheat_bot': '/.netlify/functions/run_wheat_bot',
        '/api/notes': '/.netlify/functions/notes',
        '/api/add_note': '/.netlify/functions/notes',
        '/api/delete_note': '/.netlify/functions/notes',
        '/api/news_alerts': '/.netlify/functions/news_alerts',
        '/api/news_alerts/poll': '/.netlify/functions/news_alerts',
        '/api/news_alerts/mark_read': '/.netlify/functions/news_alerts',
        '/api/quote/': '/.netlify/functions/quote',
        '/api/watchlist': '/.netlify/functions/watchlist',
    }
    
    # Replace all occurrences
    for old_route, new_route in route_map.items():
        # Handle routes with parameters
        if old_route.endswith('/'):
            pattern = old_route.replace('/', r'\/')
            content = re.sub(
                rf'["\']{pattern}([^"\']*)["\']',
                lambda m: f'"{new_route}{m.group(1)}"',
                content
            )
        else:
            content = content.replace(old_route, new_route)
    
    return content

def main():
    """Main migration function"""
    print("🔄 Migrating dashboard for Netlify deployment...")
    
    # Read source dashboard
    if not os.path.exists(SOURCE_DASHBOARD):
        print(f"❌ Source dashboard not found: {SOURCE_DASHBOARD}")
        print("   Please run this from the dashboard_netlify directory")
        return
    
    with open(SOURCE_DASHBOARD, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Migrate API calls
    content = migrate_api_calls(content)
    
    # Create public directory if needed
    os.makedirs('public', exist_ok=True)
    
    # Write migrated dashboard
    with open(TARGET_DASHBOARD, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard migrated to {TARGET_DASHBOARD}")
    print("   All API calls updated to use Netlify Functions")
    print("\n⚠️  Note: You still need to create all Netlify Functions")
    print("   See README_DEPLOY.md for details")

if __name__ == '__main__':
    main()

