# Trading Bot Dashboard - Netlify Deployment

Cloud-hosted dashboard for the Wheat Trading Bot, deployed on Netlify with Neon PostgreSQL database.

## 🎯 What This Is

A fully functional trading dashboard that:
- ✅ Tracks positions and trades
- ✅ Displays wheat bot signals
- ✅ Shows portfolio performance
- ✅ Manages notes and news alerts
- ✅ Provides market watch functionality
- ✅ **No sensitive data** - safe for public deployment

## 🚀 Quick Deploy

### Prerequisites
- Netlify account (free tier works)
- Neon PostgreSQL database (same one used for signal pager)
- GitHub account (for Git deployment)

### Steps

1. **Set up database tables** (see `README_DEPLOY.md`)
2. **Create GitHub repo**:
   ```bash
   ./setup_github.sh
   ```
   Or manually create at https://github.com/new

3. **Connect to Netlify**:
   - Go to https://app.netlify.com
   - Import from GitHub
   - Select your repository
   - Set environment variable: `NETLIFY_DATABASE_URL`

4. **Deploy!** 🎉

See `DEPLOY_VIA_GIT.md` for detailed instructions.

## 📁 Project Structure

```
dashboard_netlify/
├── netlify/
│   ├── functions/
│   │   ├── _shared/
│   │   │   └── db.py          # Neon database adapter
│   │   ├── overview.py        # Portfolio overview
│   │   ├── positions.py        # Position management
│   │   ├── trades.py           # Trade history
│   │   ├── signals.py          # Wheat bot signals
│   │   ├── close_position.py   # Close positions
│   │   ├── set_balance.py      # Set cash balance
│   │   ├── notes.py            # Notes management
│   │   ├── news_alerts.py      # News alerts
│   │   ├── quote.py            # Stock quotes
│   │   └── watchlist.py        # Watchlist quotes
├── public/
│   └── index.html              # Dashboard UI
├── netlify.toml                # Netlify configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Set in Netlify dashboard (Site settings → Environment variables):

- `NETLIFY_DATABASE_URL` - Your Neon PostgreSQL connection string

### Database Tables

All tables are created automatically on first function call. See `README_DEPLOY.md` for manual setup.

## 📊 Features

- **Portfolio Overview**: Cash balance, portfolio value, P&L stats
- **Position Management**: Add/close positions with automatic balance tracking
- **Trade History**: View all completed trades
- **Signals**: Display wheat bot trading signals
- **Notes**: Trading tips and notes
- **News Alerts**: Google Alerts integration
- **Market Watch**: Real-time stock quotes
- **Performance Tracking**: Historical performance metrics

## 🔗 API Endpoints

All endpoints are Netlify Functions:

- `/.netlify/functions/overview` - GET portfolio overview
- `/.netlify/functions/positions` - GET/POST positions
- `/.netlify/functions/trades` - GET trade history
- `/.netlify/functions/signals` - GET recent signals
- `/.netlify/functions/close_position` - POST close position
- `/.netlify/functions/set_balance` - POST set cash balance
- `/.netlify/functions/notes` - GET/POST/DELETE notes
- `/.netlify/functions/news_alerts` - GET/POST news alerts
- `/.netlify/functions/quote/:symbol` - GET stock quote
- `/.netlify/functions/watchlist` - GET watchlist quotes

## 🐛 Troubleshooting

See `DEPLOY_VIA_GIT.md` for troubleshooting guide.

## 📝 Documentation

- `README_DEPLOY.md` - Detailed deployment guide
- `DEPLOY_VIA_GIT.md` - Git deployment instructions
- `QUICK_START.md` - Quick reference

## 🔒 Security

- No authentication (public dashboard)
- No sensitive API keys stored
- All data in Neon PostgreSQL (cloud database)
- CORS enabled for all functions

## 🎉 Success!

Once deployed, your dashboard will be live at:
`https://your-site-name.netlify.app`

Enjoy your cloud-hosted trading dashboard! 🚀

